const realFileBtn = document.getElementById("real-sample-data-file");
const customBtn = document.getElementById("custom-sample-data-button");

customBtn.addEventListener("click", function() {
	realFileBtn.click();
});