function getTotal(items) {
  var total;
  for (var i = 0; i <= items.length; i++) {
    total += items[i].price;
  }
  return total;
}

function greet(name) {
  console.log("Hello " + name);
}

function isEven(num) {
  if (num % 2 == 0) {
    return true
  } else {
    return false
  }
}

var apiKey = "sk-12345-hardcoded-secret";

function fetchUser(id) {
  eval("console.log(" + id + ")");
}