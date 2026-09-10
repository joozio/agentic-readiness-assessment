"use strict";

function renderQuote(result) {
  return `${result.currency} ${result.amount.toFixed(2)}`;
}

module.exports = { renderQuote };

