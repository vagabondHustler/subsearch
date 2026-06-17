import fs from "fs";
import { globbyStream } from "globby";
import { MaxRectsPacker } from "maxrects-packer";
import path, { dirname } from "path";
import sharp from "sharp";
import { fileURLToPath } from 'url';

const stylesPath = "../../src/subsearch/gui/resources/styles"
const assetsPath = "../../src/subsearch/gui/resources/assets"
const scriptPath = fileURLToPath(import.meta.url);
const scriptDirectoryPath = dirname(scriptPath);
const spritesTclPath = path.join(scriptDirectoryPath, stylesPath, "sprites.tcl");
const spritesheetPngPath = path.join(scriptDirectoryPath, assetsPath, "spritesheet.png");

const targetExtension = ".png"
const inputImages = ".input";
const inputDirPath = path.join(scriptDirectoryPath, inputImages);

if (!fs.existsSync(inputDirPath)) {
	console.error(`Error: The '${inputDirPath}' directory does not exist.`);;
	fs.mkdirSync(inputDirPath);
	console.log("Directory created.");
	console.log("Process exiting.");
	process.exit();
} else {
	console.log("Input directory exists.");
}

console.log("Reading files from the input directory");
fs.readdir(inputDirPath, (err, files) => {
	if (err) {
		console.error("Error reading directory:", err);
		console.log("Process exiting.");
		process.exit();
	}

	const filteredFiles = files.filter(file => path.extname(file) === targetExtension);
	const fileCount = filteredFiles.length;
	if (fileCount == 0) {
		console.error(`Error: The '${inputDirPath}' directory is empty.`);
		console.log("Process exiting.");
		process.exit();
	} else {
		console.log(`Number of ${targetExtension} files in the directory: ${fileCount}`);
	}
});


const packer = new MaxRectsPacker(Infinity, Infinity, 0, {
	pot: false,
	square: false,
});

let images = [];

for await (const path of globbyStream(`${inputImages}/*.png`)) {
	const delimiter = "/";
	const pathArray = path.split(delimiter);
	const collectedFile = pathArray[pathArray.length - 1];
	console.log(`Collected sprite: ${collectedFile}`);
	images.push(path);
}
packer.addArray(
	await Promise.all(
		images.map(async (f) => {
			const p = f;
			const { width, height } = await sharp(p).metadata();
			const imagePath = f;
			return {
				width,
				height,
				imagePath,
			};
		})
	)
);

const packedBin = packer.bins[0];

const packedImage = await sharp({
	create: {
		width: packedBin.width,
		height: packedBin.height,
		channels: 4,
		background: "transparent",
	},
})
	.composite(
		packedBin.rects.map((e) => ({
			input: e.imagePath,
			left: e.x,
			top: e.y,
		}))
	)
	.png({
		compressionLevel: 9,
	})
	.toBuffer();
const spritedata = packedBin.rects
	.map((e) => {
		const { name } = path.parse(e.imagePath);
		const { x, y, width, height } = e;
		return `  ${name} ${x} ${y} ${width} ${height} \\\n`;
	})
	.join("");

const spriteDataTcl = `set ::sprite_data [list \\\n${spritedata}]\n`;

fs.writeFileSync(`${spritesTclPath}`, spriteDataTcl);
console.log(`Sprite data written to ${spritesTclPath}`);
fs.writeFileSync(`${spritesheetPngPath}`, packedImage);
console.log(`Packed image written to ${spritesheetPngPath}`);
console.log("Process exiting.");