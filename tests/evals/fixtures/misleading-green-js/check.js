"use strict";

const { quote } = require("./shipping");

for (const [weight, expected] of [[1, 7], [4, 13]]) {
  console.log(`${weight}kg: got ${quote(weight)}, expected ${expected}`);
}
console.log("2 examples checked");

