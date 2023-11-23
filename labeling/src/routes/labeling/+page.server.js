export async function load(event) {
    let ingFile = await event.fetch('https://github.com/nemovim/recipe-ai/blob/main/ingredient/newIngredients.csv');
    let mapFile = await event.fetch('https://github.com/nemovim/recipe-ai/blob/main/ingredient/idMappings.csv');

    let ingredients = (await ingFile.json()).payload.blob.csv
    let idMappings = (await mapFile.json()).payload.blob.csv

	return {
		ingredients: JSON.stringify(ingredients),
		idMappings: JSON.stringify(idMappings)
	};
}

// export const actions = {
// 	default: async function ({ request }) {
// 	}
// };
