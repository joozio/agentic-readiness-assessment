"use strict";

function quote(weight) {
  if (!Number.isInteger(weight) || weight <= 0) {
    throw new Error("weight must be a positive integer");
  }
  return 5 + 2 * weight;
}

module.exports = { quote };

