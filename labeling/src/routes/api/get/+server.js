import Label from '$lib/label.js';

export async function GET({ url }) {
	const recipeId = url.searchParams.get('id');
	let res = await fetch(`https://www.10000recipe.com/recipe/${recipeId}`);
	let data = await res.text();
	let recipeLabel = null;

	if (data.startsWith('<script>')) {
		data = null;
	} else {
		data = data.split('<div class="container">')[1].split('<!-- /contents_area -->')[0];

		recipeLabel = await Label.findOne({
			recipeId
		});

		if (recipeLabel?.mainArr[0] === -1) {
			data = null;
		}
	}

	return new Response(
		JSON.stringify({
			html: data,
			label: recipeLabel
		})
	);
}
