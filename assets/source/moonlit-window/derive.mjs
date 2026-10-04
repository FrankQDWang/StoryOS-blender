import sharp from '../../../tools/book-check/node_modules/sharp/dist/index.mjs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const dir = path.dirname(fileURLToPath(import.meta.url));
const source = path.join(dir, 'source.png');
// Native ImageGen boundaries are x873/y368. Exclude seam pixels and
// preserve the moon's square proportions while packing exact runtime tiles.
const sky = await sharp(source).extract({ left: 0, top: 0, width: 871, height: 1254 }).resize(768, 1024, { fit: 'fill' }).toBuffer();
const moon = await sharp(source).extract({ left: 884, top: 0, width: 368, height: 368 }).resize(256, 256, { fit: 'fill' }).toBuffer();
const bark = await sharp(source).extract({ left: 875, top: 370, width: 379, height: 884 }).resize(256, 768, { fit: 'fill' }).toBuffer();
const packed = await sharp({ create: { width: 1024, height: 1024, channels: 3, background: '#000000' } }).composite([{ input: sky, left: 0, top: 0 }, { input: moon, left: 768, top: 0 }, { input: bark, left: 768, top: 256 }]).png().toBuffer();
await sharp(packed).removeAlpha().png().toFile(path.join(dir, 'atlas.png'));
await sharp(packed).removeAlpha().webp({ lossless: true }).toFile(path.join(dir, 'atlas.webp'));
