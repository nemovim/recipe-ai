import Label from '$lib/label.js';

export async function GET({ url }) {
	const recipeId = url.searchParams.get('id');

	let recipeLabel = await Label.findOne({
		recipeId
	});

	if (recipeLabel === null) {
		recipeLabel = new Label({
			recipeId,
			mainArr: [-1]
		});
	} else {
		recipeLabel.mainArr = [-1];
	}

	await recipeLabel.save();

	return new Response(
		JSON.stringify({
			success: true
		})
	);
}
