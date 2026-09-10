"use strict";

const assert = require("assert");
const { renderQuote } = require("./render");

assert.strictEqual(renderQuote({ currency: "USD", amount: 13 }), "USD 13.00");
assert.strictEqual(renderQuote({ currency: "EUR", amount: 7.5 }), "EUR 7.50");
console.log("2 widget checks passed");

