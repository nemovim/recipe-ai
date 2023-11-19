<script>
	import { onMount } from 'svelte';

	export let data;
	export let form;

	const ingredientIdMap = new Map(JSON.parse(data.ingredients));

	let originalHTML = '';
	let recipeId = 6900000;
	let ingredientType = '0';
	let ingredientIdArr = [];

	let recipeTitle = '';
	let ingredientNameArr = [];
	let mainImg = '';

	async function getRecipe(id) {
		let res = await fetch(`/api?id=${id}`);
		originalHTML = await res.text();
		recipeId = id;

		preview();
	}

	function preview() {
		document.getElementById('originalDiv').innerHTML = originalHTML;

		recipeTitle = document.querySelector('.view2_summary > h3').outerHTML;

		mainImg = document.getElementById('main_thumbs').outerHTML;

		let ingredientHTMLArr = document.querySelectorAll(
			'#divConfirmedMaterialArea li > a:first-child'
		);
		ingredientHTMLArr.forEach((a, b) => {
			ingredientNameArr.push(a.outerHTML);
			ingredientIdArr.push(a.getAttribute('href').split("'")[1]);
		});

		ingredientIdArr = [...ingredientIdArr];
		ingredientNameArr = [...ingredientNameArr];
	}

	let isStarted = false;
	let startRecipeId = recipeId;

	async function startLabeling() {
		await getRecipe(startRecipeId);
		isStarted = true;
	}

    function stopLabeling() {
        isStarted = false;
        recipeTitle = '';
        ingredientNameArr = [];
        mainImg = '';
    }

	onMount(async () => {
		if (form?.success) {
			startRecipeId = form.nextId;
            ingredientType = String(form.nextType);
			await startLabeling();
		}
	});
</script>

<h1 id="title">Welcome to the <span style="color:red">HELL</span> of labeling!</h1>

<section id="mainSection">
	<div id="labelingDiv">
		{#if !isStarted}
			<input id="recipeId" type="number" placeholder={recipeId} bind:value={startRecipeId} />
			<select bind:value={ingredientType}>
				<option value="0" selected>주재료</option>
				<option value="1">조미료</option>
				<option value="2">향신료</option>
			</select>
			<button on:click={startLabeling}>시작하기</button>
		{:else}
			<form method="post">
				<p>라벨링하는 타입 (0: 주재료 / 1: 조미료 / 2: 향신료):</p>
				<input type="number" readonly value={ingredientType} name="ingredientType" />
				<p>라벨링하는 레시피 아이디:</p>
				<input type="number" readonly value={recipeId} name="recipeId" />
				<hr />
				<div class="ingredientsDiv">
					{#each ingredientIdArr as ingredient, i}
						<div>
							<label for="ingredient-{i}">{ingredientIdMap.get(ingredient)}</label>
							<input id="ingredient-{i}" name="ingredient-{ingredient}" type="checkbox" />
						</div>
					{/each}
                    <input type="text" readonly value={ingredientIdArr.join('/')} name="ingredientIds" style="display:none">
				</div>
				<button>확인</button>
			</form>
				<button on:click={stopLabeling}>취소</button>
		{/if}
	</div>

	<div id="previewDiv">
		{@html recipeTitle}
		<div class="ingredientsDiv">
			{#each ingredientNameArr as ingredient}
				<p>{@html ingredient}</p>
			{/each}
		</div>
		{@html mainImg}
	</div>
</section>

<div id="originalDiv"></div>

<style lang="scss">
	* {
		font-size: 1.4rem;
	}

	#title {
		padding: 2rem;
		font-size: 3rem;

		span {
			font-size: 3rem;
		}
	}

	#mainSection {
		background-color: white;
		margin: 2rem;
		margin-top: 0;
		padding: 2rem;
		border: 0.2rem solid black;
		display: flex;
		justify-content: space-between;

		#labelingDiv {
			width: 50%;
			padding: 1rem;

			form {
				display: flex;
				flex-direction: column;
			}

			div {
				padding: 1rem;
			}

			label {
				border: solid 0.1rem black;
				padding: 0.5rem;
			}

			label:hover,
			input {
				cursor: pointer;
				background-color: rgb(245, 245, 245);
			}

			button {
				margin-top: 2rem;
			}
		}

		#previewDiv {
			width: 50%;
			padding: 1rem;

			:global(img) {
				width: -webkit-fill-available;
			}
		}
	}

	.ingredientsDiv {
		display: flex;
		flex-wrap: wrap;

		* {
			min-width: max-content;
		}
	}

	hr {
		margin: 2rem 0;
	}

	#originalDiv {
		display: none;
	}
</style>
