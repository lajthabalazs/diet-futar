function incrementQuantity(id)
{
	textField = document.getElementById(id);
	stringValue=textField.value;
	if (isNaN(stringValue)) {
		value = 0;
	} else {
		value = parseInt(stringValue);
		value = value + 1;
	}
	textField.value = value;
}

function decrementQuantity(id)
{
	textField = document.getElementById(id);
	stringValue=textField.value;
	if (isNaN(stringValue)) {
		value = 0;
	} else {
		value = parseInt(stringValue);
		value = value - 1;
	}
	textField.value = value;
}

function validateQuantity(id)
{
	textField = document.getElementById(id);
	stringValue=textField.value;
	if (stringValue == "" || isNaN(stringValue)) {
		value = 0;
	} else {
		value = parseInt(stringValue);
	}
	textField.value = value;
}

function decrementQuantityNotNegative(id)
{
	textField = document.getElementById(id);
	stringValue=textField.value;
	if (isNaN(stringValue)) {
		value = 0;
	} else {
		value = parseInt(stringValue);
		value = value - 1;
	}
	if (value < 0) {
		value = 0;
	}
	textField.value = value;
}

function validateQuantityNotNegative(id)
{
	textField = document.getElementById(id);
	stringValue=textField.value;
	if (stringValue == "" || isNaN(stringValue)) {
		value = 0;
	} else {
		value = parseInt(stringValue);
	}
	if (value < 0) {
		value = 0;
	}
	textField.value = value;
}