function incrementQuantity(id)
{
	textField = document.getElementById(id);
	value = parseInt(textField.value);
	value = value + 1;
	textField.value = value;
}

function decrementQuantity(id)
{
	textField = document.getElementById(id);
	value = parseInt(textField.value);
	value = value - 1;
	textField.value = value;
}

function validateQuantity(id)
{
	textField = document.getElementById(id);
	value = parseInt(textField.value);
	value = value;
	textField.value = value;
}