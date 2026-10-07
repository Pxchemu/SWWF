// Wykonuje skrypt SkyPredict (warnings.php) DOKLADNIE tak jak strona: podmienia putPolygon,
// wywoluje applyData({}) i wypisuje zebrane polygony jako JSON na stdout.
//
// Uruchamiac z ograniczeniami Node (bez zapisu plikow, sieci i procesow), bo wykonuje cudzy kod:
//   node --permission --allow-fs-read="$PWD/sky_raw.js" sky_eval.js sky_raw.js > sky_polygons.json
// Plik skryptu SkyPredict jest wczesniej pobrany osobnym krokiem (curl).
const fs = require("fs");
const vm = require("vm");

const file = process.argv[2];
const code = fs.readFileSync(file, "utf8");
const out = [];

const sandbox = {
  putPolygon: (mapVar, type, level, validFrom, validTo, content, color, coords) => {
    out.push({
      type: String(type),
      level: parseInt(level, 10),
      validFrom: String(validFrom),
      validTo: String(validTo),
      content: String(content || ""),
      color: String(color || ""),
      coords,
    });
  },
};
vm.createContext(sandbox);
try {
  vm.runInContext(code, sandbox, { timeout: 5000 });
  if (typeof sandbox.applyData === "function") sandbox.applyData({});
} catch (e) {
  // strona tez ignoruje bledy w applyData i bierze to, co zdazylo sie zebrac
  process.stderr.write("Ostrzezenie: " + (e && e.message ? e.message : e) + "\n");
}
process.stdout.write(JSON.stringify(out));
