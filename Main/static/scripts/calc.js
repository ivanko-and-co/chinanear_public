const quantityQuan = document.getElementById("quantityQuan");
const quantityPrice = document.getElementById("quantityPrice");
const quantityValue = document.getElementById("quantityTotal");

const calculate = () => {
  const value1 = Number(quantityQuan.value);
  const value2 = Number(quantityPrice.value);
  return value1 * value2;
};

quantityQuan.addEventListener("input", () => {
  quantityValue.value = calculate();
  console.log(quantityQuan, quantityPrice, quantityValue);
});

quantityPrice.addEventListener("input", () => {
  quantityValue.value = calculate();
  console.log(quantityQuan, quantityPrice, quantityValue);
});
