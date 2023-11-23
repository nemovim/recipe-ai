<script>
	import { onMount } from 'svelte';
	import { parse } from 'node-html-parser';

	export let data;

	const ingredientIdMap = new Map(JSON.parse(data.ingredients));
	const changedIdMap = new Map(JSON.parse(data.idMappings));

	let startRecipeId = 6900000;
	const loadCnt = 5;

	let currentRecipeId = 6900000;
	let currentIngredientType = '0';

	let showRecipeId;
	let recipeLabel;
	let recipeTitle = '';
	let recipeImg = '';
	let ingredientIdArr = [];
	let ingredientNameArr = [];
	let checkboxArr = [];

	let isLoading = false;

	let recipeDataMap = new Map();

	async function fillRecipeDataMap(startId, endId) {
		let taskIdArr = [];
		let taskArr = [];

		for (let id = startId; id <= endId; id++) {
			if (!recipeDataMap.has(id)) {
				taskIdArr.push(id);
				taskArr.push(
					new Promise((resolve) => {
						resolve(loadRecipe(id));
					})
				);
			}
		}

		let result = await Promise.allSettled(taskArr);

		result.forEach((recipeData, i) => {
			recipeDataMap.set(taskIdArr[i], recipeData.value);
		});
	}

	async function loadRecipe(id) {
		let res = await fetch(`/api/get?id=${id}`);
		let data = JSON.parse(await res.text());

		if (data.html === '' || data.html === null) {
			return null;
		} else {
			let extractedData = await extractData(data.html);

			if (extractedData === null) {
				return null;
			} else {
				return {
					id: id,
					label: data.label,
					...extractedData
				};
			}
		}
	}

	async function extractData(html) {
		let parsedHTML = parse(html);

		let title = parsedHTML.querySelector('.view2_summary > h3').textContent;

		let ingredientHTMLArr = parsedHTML.querySelectorAll('#divConfirmedMaterialArea ul > a');

		let _ingredientNameArr = [];
		let _ingredientIdArr = [];

		ingredientHTMLArr.forEach((ingredient, i) => {
			_ingredientNameArr.push(ingredient.textContent.replaceAll('\n', '').trim().split('   ')[0]);
			_ingredientIdArr.push(ingredient.getAttribute('href').split("'")[1]);
		});

		let ingredientIdSet = new Set(
			_ingredientIdArr.map((id) => {
				return changedIdMap.get(id);
			})
		);

		if (ingredientIdSet.has(undefined)) {
			return null;
		}

		_ingredientIdArr = Array(...ingredientIdSet);

		let img = parsedHTML.querySelector('#main_thumbs').toString();

		return {
			title,
			ingId: _ingredientIdArr,
			ingName: _ingredientNameArr,
			img
		};
	}

	function getTypeArr(ingredientId) {
		if (recipeLabel === null) {
			return '';
		}

		ingredientId = Number(ingredientId);

		let typeArr = [];
		if (recipeLabel.mainArr.indexOf(ingredientId) !== -1) {
			typeArr.push('main');
		}
		if (recipeLabel.spiceArr.indexOf(ingredientId) !== -1) {
			typeArr.push('spice');
		}
		if (recipeLabel.condimentArr.indexOf(ingredientId) !== -1) {
			typeArr.push('condiment');
		}

		return typeArr;
	}

	async function getRecipe(id, delta) {
		if (recipeDataMap.get(id) === undefined) {
			await fillRecipeDataMap(id - loadCnt, id + loadCnt);
			return await getRecipe(id, delta);
		} else if (recipeDataMap.get(id) === null) {
			return await getRecipe(id + delta, delta);
		} else {
			return recipeDataMap.get(id);
		}
	}

	async function showRecipe(id, delta) {
		let recipeData = await getRecipe(id, delta);

		currentRecipeId = recipeData.id;
		showRecipeId = recipeData.id;

		recipeLabel = recipeData.label;
		recipeTitle = recipeData.title;
		ingredientIdArr = recipeData.ingId;
		ingredientNameArr = recipeData.ingName;
		recipeImg = recipeData.img;

		checkboxArr = Array(ingredientIdArr.length).fill(false);
	}

	async function nextRecipe(id) {
		isLoading = true;
		await showRecipe(id + 1, +1);
		isLoading = false;
		fillRecipeDataMap(currentRecipeId - loadCnt, currentRecipeId + loadCnt);
	}

	async function previousRecipe(id) {
		isLoading = true;
		await showRecipe(id - 1, -1);
		isLoading = false;
		fillRecipeDataMap(currentRecipeId - loadCnt, currentRecipeId + loadCnt);
	}

	async function deleteRecipe(id) {
		if (confirm('정말로 삭제하시겠습니까?')) {
			isLoading = true;
			await fetch(`/api/delete?id=${id}`);
			recipeDataMap.set(id, null);
			await nextRecipe(id);
		}
	}

	async function changeRecipe(id) {
		isLoading = true;
		await fillRecipeDataMap(id - loadCnt, id + loadCnt);
		await showRecipe(id, +1);
		isLoading = false;
	}

	async function saveRecipe() {

		let data = {
			recipeId: currentRecipeId,
			ingredientType: currentIngredientType,
			ingredientIds: ingredientIdArr.join('/'),
			checkbox: checkboxArr
		}

		fetch(`/api/set`, {
			method: 'POST',
			body: JSON.stringify(data),
			headers: {
				'Content-Type': 'application/json',
			}
		});

		recipeDataMap.set(currentRecipeId, loadRecipe(currentRecipeId));

		nextRecipe(currentRecipeId);
	}

	onMount(async () => {
		isLoading = true;
		await changeRecipe(startRecipeId);
		isLoading = false;
	});
</script>

<h1 id="title">Welcome to the <span style="color:red">HELL</span> of labeling!</h1>

<section id="mainSection">
	{#if isLoading}
		<p><b>Loading...</b></p>
	{:else}
			<div id="leftDiv">
				<div id="haederDiv">
					<p>라벨링하는 타입:</p>
					<select bind:value={currentIngredientType} name="ingredientType">
						<option value="0" selected>주재료</option>
						<option value="1">조미료</option>
						<option value="2">향신료</option>
					</select>
					<p>라벨링하는 레시피 아이디:</p>
					<input type="number" bind:value={showRecipeId} name="recipeId" />
					<button on:click={changeRecipe(showRecipeId)}>레시피 변경</button>
				</div>
				<hr />
				<div id="previewDiv">
					<h1>{recipeTitle}</h1>
					<div>
						{#each ingredientNameArr as ingredientName}
							<p>{ingredientName}</p>
						{/each}
					</div>
					{@html recipeImg}
				</div>
			</div>

			<div id="rightDiv">
				<div id="ingredientsDiv">
					<p>재료들:</p>
					<div>
						{#each ingredientIdArr as ingredientId, i}
							<div>
								<label for="ingredient-{i}"
									>{ingredientIdMap.get(ingredientId)}
									{#each getTypeArr(ingredientId) as type}
										<b class={type}></b>
									{/each}
								</label>
								<input id="ingredient-{i}" name="ingredient-{ingredientId}" type="checkbox" bind:checked={checkboxArr[i]}/>
							</div>
						{/each}
					</div>
					<input
						type="text"
						readonly
						value={ingredientIdArr.join('/')}
						name="ingredientIds"
						style="display:none"
					/>
				</div>

				<div id="btnDiv">
					<button on:click={saveRecipe}><b>저장</b></button>
					<button on:click={previousRecipe(currentRecipeId)}>이전</button>
					<button on:click={nextRecipe(currentRecipeId)}>다음</button>
					<button on:click={deleteRecipe(currentRecipeId)}>삭제</button>
				</div>
			</div>
	{/if}
</section>

<style lang="scss">
	* {
		font-size: 1.4rem;
	}

	#title {
		padding: 1rem 2rem;
		font-size: 2rem;

		span {
			font-size: 3rem;
		}
	}

	#mainSection {
		background-color: white;
		margin: 2rem;
		margin-top: 0;
		padding: 1rem;
		border: 0.2rem solid black;
		display: flex;


		#leftDiv {
			padding: 1rem;
			width: 35%;

			#headerDiv {
				display: flex;
				flex-direction: column;
			}

			hr {
				margin: 1rem 0;
			}

			#previewDiv {
				div {
					display: flex;
					flex-wrap: wrap;

					p {
						margin-right: 0.5rem;
					}
				}

				:global(img) {
					max-width: -webkit-fill-available;
					max-height: 40vh;
				}
			}
		}

		#rightDiv {
			padding: 1rem;
			width: 65%;
			display: flex;
			flex-direction: column;

			#ingredientsDiv {
				div {
					display: flex;
					flex-wrap: wrap;
					margin: 1rem 0;

					div {
						margin-right: 1.5rem;
						label {
							display: inline-block;
							border: solid 0.1rem black;
							padding: 0.5rem;
							margin-right: 0.5rem;
						}
					}
				}
			}
		}
	}

	#originalDiv {
		display: none;
	}

	#btnDiv {
		display: flex;
		justify-content: space-between;

		button {
			width: 20%;
		}
	}

	label:hover,
	input:hover {
		cursor: pointer;
		background-color: rgb(245, 245, 245);
	}

	:global(.main)::after {
		content: '메인';
		background-color: rgb(230, 230, 255);
	}
	:global(.condiment)::after {
		content: '맛';
		background-color: rgb(255, 255, 200);
	}
	:global(.spice)::after {
		content: '향';
		background-color: rgb(255, 220, 220);
	}
</style>
