const ExcelJS = require('exceljs');
const fs = require('fs');
const path = require('path');

const EXCEL_PATH = 'c:/Users/jiaoj/Downloads/VSCode開発環境構築手順書_Oracle版.xlsx';
const IMG_DIR = 'Liu/vscode_oracle_img';
const MD_PATH = 'Liu/VSCode開発環境構築手順書_Oracle版.md';

// 画像フォルダ作成
if (!fs.existsSync(IMG_DIR)) {
  fs.mkdirSync(IMG_DIR, { recursive: true });
}

async function main() {
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(EXCEL_PATH);

  // 全画像を抽出（シート名と画像インデックスで管理）
  const imageMap = {}; // sheetName -> [{filename, row, col}]

  workbook.worksheets.forEach((sheet) => {
    const imgs = sheet.getImages();
    if (imgs.length > 0) {
      imageMap[sheet.name] = [];
      imgs.forEach((imgRef, idx) => {
        const img = workbook.model.media.find(m => m.index === imgRef.imageId);
        if (!img) return;
        const ext = img.extension || 'png';
        const safeSheetName = sheet.name.replace(/[^\w\u3000-\u9fff\u30a0-\u30ff\u3040-\u309f]/g, '_');
        const filename = `${safeSheetName}_${idx + 1}.${ext}`;
        const filepath = path.join(IMG_DIR, filename);
        fs.writeFileSync(filepath, img.buffer);
        console.log(`  画像保存: ${filepath}`);

        // 画像の位置（行）を取得
        const rowStart = imgRef.range && imgRef.range.tl ? imgRef.range.tl.nativeRow : 0;
        imageMap[sheet.name].push({ filename, row: rowStart, col: 0 });
      });
    }
  });

  // Markdown生成
  let md = '# VSCode開発環境構築手順書（Oracle版）\n\n';

  const sheetOrder = [
    '資料作成時のバージョン情報',
    '前提条件',
    '既存プロジェクトVSCode対応',
    '起動後～拡張機能インストール',
    'DB定義にかんするTSVファイルの出力',
    'テーブル定義の生成',
    'DB構築',
    'dbfluteのjarファイルの生成',
    'プロジェクト(フォルダ)を開く',
    'DB接続情報設定',
    '環境構築',
    'Tomcat調整',
    'デバッグ',
    '成功確認',
    '環境削除',
    'VSCodeアンインストール',
    'トラブルＱＡ',
  ];

  // 目次
  md += '## 目次\n\n';
  workbook.worksheets.forEach((sheet) => {
    const anchor = sheet.name.replace(/\s/g, '-');
    md += `- [${sheet.name}](#${anchor})\n`;
  });
  md += '\n---\n\n';

  workbook.worksheets.forEach((sheet) => {
    console.log(`シート処理中: ${sheet.name}`);
    md += `## ${sheet.name}\n\n`;

    const sheetImages = imageMap[sheet.name] || [];
    let imageInserted = new Set();

    // シート内の行を処理
    sheet.eachRow({ includeEmpty: false }, (row, rowNumber) => {
      // この行より前に挿入すべき画像があるか
      sheetImages.forEach((imgInfo, imgIdx) => {
        if (!imageInserted.has(imgIdx) && imgInfo.row < rowNumber && imgInfo.row >= (rowNumber - 5)) {
          md += `\n![${imgInfo.filename}](./vscode_oracle_img/${imgInfo.filename})\n\n`;
          imageInserted.add(imgIdx);
        }
      });

      // 行のセルを結合してテキスト取得
      const cells = [];
      row.eachCell({ includeEmpty: false }, (cell) => {
        const val = cell.value;
        if (val === null || val === undefined) return;
        let text = '';
        if (typeof val === 'object' && val.richText) {
          text = val.richText.map(r => r.text).join('');
        } else if (typeof val === 'object' && val.text) {
          text = val.text;
        } else if (typeof val === 'object' && val.hyperlink) {
          text = val.hyperlink;
        } else {
          text = String(val);
        }
        text = text.trim();
        if (text) cells.push(text);
      });

      if (cells.length === 0) return;

      const firstCell = cells[0];
      const indent = getIndent(row, sheet);
      const lineText = cells.join('　');

      // 見出し判定
      if (isHeading1(firstCell)) {
        md += `### ${lineText}\n\n`;
      } else if (isHeading2(firstCell)) {
        md += `#### ${lineText}\n\n`;
      } else if (indent >= 2) {
        md += `    - ${lineText}\n`;
      } else if (indent === 1) {
        md += `- ${lineText}\n`;
      } else {
        md += `${lineText}\n\n`;
      }
    });

    // 末尾の画像
    sheetImages.forEach((imgInfo, imgIdx) => {
      if (!imageInserted.has(imgIdx)) {
        md += `\n![${imgInfo.filename}](./vscode_oracle_img/${imgInfo.filename})\n\n`;
        imageInserted.add(imgIdx);
      }
    });

    md += '\n---\n\n';
  });

  fs.writeFileSync(MD_PATH, md, 'utf8');
  console.log(`\nMarkdown生成完了: ${MD_PATH}`);
  console.log(`抽出画像数: ${Object.values(imageMap).flat().length}`);
}

function getIndent(row, sheet) {
  // 最初の非空セルの列番号でインデントを推定
  let firstCol = 99;
  row.eachCell({ includeEmpty: false }, (cell) => {
    if (cell.col < firstCol) firstCol = cell.col;
  });
  if (firstCol <= 1) return 0;
  if (firstCol === 2) return 1;
  return 2;
}

function isHeading1(text) {
  return /^[１２３４５６７８９\d][\．\.\s]/.test(text) ||
         /^[一二三四五六七八九十][\．\.\s]/.test(text);
}

function isHeading2(text) {
  return /^[①②③④⑤⑥⑦⑧⑨⑩]/.test(text);
}

main().catch(e => {
  console.error('エラー:', e);
  process.exit(1);
});