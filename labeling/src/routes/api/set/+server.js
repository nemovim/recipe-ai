import Label from '$lib/label.js';

export async function POST({ request }) {
	const data = await request.json();

	const recipeId = Number(data.recipeId);

	let label = await Label.findOne({
		recipeId
	});

	if (label === null) {
		label = new Label();
		label.recipeId = recipeId;
	}

	label.ingredientArr = data.ingredientIds
		.split('/')
		.map((value) => Number(value));

	let dataArr = data.checkbox.map((val, idx) => {
		if (val) {
			return label.ingredientArr[idx];
		}
	});

	const ingredientType = Number(data.ingredientType);

	if (ingredientType === 0) {
		label.mainArr = dataArr;
	} else if (ingredientType === 1) {
		label.condimentArr = dataArr;
	} else {
		label.spiceArr = dataArr;
	}

	await label.save();

	return new Response(
		JSON.stringify({
			success: true,
			nextType: ingredientType,
			nextId: recipeId + 1
		})
	);
}
