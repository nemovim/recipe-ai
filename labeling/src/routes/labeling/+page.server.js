import Label from '$lib/label.js';

export async function load(event) {
    let ingFile = await event.fetch('ingredients.csv');
    let ingredients = (await ingFile.text()).split('\r\n');
	return {
		ingredients: JSON.stringify(ingredients)
	};
}

export const actions = {
	default: async function ({ request }) {
		const data = await request.formData();
		const recipeId = Number(data.get('recipeId'));
		let label = await Label.findOne({
			recipeId
		});

		if (label === null) {
			label = new Label();
			label.recipeId = recipeId;
		}

        label.ingredientArr = data.get('ingredientIds').split('/').map(value => Number(value));

		let dataArr = [];
		data.forEach((dataValue, dataName) => {
			if (dataName !== 'recipeId' && dataName !== 'ingredientType' && dataName !== 'ingredientIds') {
				dataArr.push(Number(dataName.split('-')[1]));
			}
		});

		const ingredientType = Number(data.get('ingredientType'));

		if (ingredientType === 0) {
			label.mainArr = dataArr;
		} else if (ingredientType === 1) {
			label.seasoningArr = dataArr;
		} else {
			label.spiceArr = dataArr;
		}

		await label.save();

		return {
			success: true,
            nextType: ingredientType,
			nextId: recipeId + 1
		};
	}
};
