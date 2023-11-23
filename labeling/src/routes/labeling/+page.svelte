<script>
	import { onMount } from 'svelte';

	export let data;
	export let form;

	const ingredientIdMap = new Map(JSON.parse(data.ingredients));
	const changedIdMap = new Map(JSON.parse(data.idMappings));

	let originalHTML = '';
	let recipeId = 6900000;
	let recipeLabel = {};
	let ingredientType = '0';
	let ingredientIdArr = [];

	let recipeTitle = '';
	let ingredientNameArr = [];
	let mainImg = '';

	let isLoading = false;
	async function getRecipe(id, delta) {

		id += delta;

		isLoading = true;

		recipeTitle = '';
		ingredientNameArr = [];
		ingredientIdArr = [];
		mainImg = '';

		recipeId = id;

		let res = await fetch(`/api/get?id=${id}`);
		let data = JSON.parse(await res.text());

		originalHTML = data.html;
		recipeLabel = data.label;

		if (originalHTML === '' || originalHTML === null) {
			await getRecipe(id, delta);
		} else {
			if (!preview()) {
				await getRecipe(id, delta);
			}

			isLoading = false;
		}
	}

	function preview() {
		document.getElementById('originalDiv').innerHTML = originalHTML;

		recipeTitle = document.querySelector('.view2_summary > h3').outerHTML;

		let ingredientHTMLArr = document.querySelectorAll(
			'#divConfirmedMaterialArea li > a:first-child'
		);

		ingredientHTMLArr.forEach((a, b) => {
			ingredientNameArr.push(a.outerHTML);
			ingredientIdArr.push(a.getAttribute('href').split("'")[1]);
		});

		let ingredientIdSet = new Set(
			ingredientIdArr.map((id) => {
				return changedIdMap.get(id);
			})
		);

		if (ingredientIdSet.has(undefined)) {
			return false;
		}

		ingredientIdArr = Array(...ingredientIdSet);

		mainImg = document.getElementById('main_thumbs').outerHTML;

		ingredientNameArr = [...ingredientNameArr];

		return true;
	}

	let isStarted = false;
	let startRecipeId = recipeId;

	async function startLabeling() {
		isStarted = true;
		await getRecipe(startRecipeId-1, +1);
	}

	function onEnter(e) {
		if (e.key === 'Enter') {
			if (!isStarted) {
				startLabeling();
			}
		}
	}

	function stopLabeling() {
		isStarted = false;
		recipeTitle = '';
		ingredientNameArr = [];
		ingredientIdArr = [];
		mainImg = '';
	}

	function getTypeArr(ingredientId) {
		if (recipeLabel === null) {
			return '';
		}

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

	onMount(async () => {
		if (form?.success) {
			startRecipeId = form.nextId;
			ingredientType = String(form.nextType);
			await startLabeling();
		}
	});

	function nextRecipe() {
		getRecipe(recipeId, +1);
	}

	function previousRecipe() {
		getRecipe(recipeId, -1);
	}

	async function deleteRecipe(id) {
		let res = await fetch(`/api/delete?id=${id}`);
		// let data = JSON.parse(await res.json());
		await getRecipe(recipeId, +1);
	}
</script>

<h1 id="title">Welcome to the <span style="color:red">HELL</span> of labeling!</h1>

<section id="mainSection">
	<div id="labelingDiv">
		{#if !isStarted}
			<input
				id="recipeId"
				type="number"
				placeholder={recipeId}
				bind:value={startRecipeId}
				on:keydown={onEnter}
			/>
			<select bind:value={ingredientType} on:keydown={onEnter}>
				<option value="0" selected>주재료</option>
				<option value="1">조미료</option>
				<option value="2">향신료</option>
			</select>
			<button on:click={startLabeling} on:keydown={onEnter}>시작하기</button>
		{:else if isLoading}
			<p><b>Loading...</b></p>
		{:else}
			<form method="post">
				<p>라벨링하는 타입 (0: 주재료 / 1: 조미료 / 2: 향신료):</p>
				<input type="number" readonly value={ingredientType} name="ingredientType" />
				<p>라벨링하는 레시피 아이디:</p>
				<input type="number" readonly value={recipeId} name="recipeId" />
				<hr />
				<div class="ingredientsDiv">
					{#each ingredientIdArr as ingredientId, i}
						<div>
							<label for="ingredient-{i}"
								>{ingredientIdMap.get(ingredientId)}
								{#each getTypeArr(Number(ingredientId)) as type}
									<b class={type}></b>
								{/each}
							</label>
							<input id="ingredient-{i}" name="ingredient-{ingredientId}" type="checkbox" />
						</div>
					{/each}
					<input
						type="text"
						readonly
						value={ingredientIdArr.join('/')}
						name="ingredientIds"
						style="display:none"
					/>
				</div>
				<button>저장</button>
			</form>
			<div id="btnDiv">
				<button on:click={stopLabeling}>취소</button>
				<button on:click={previousRecipe}>이전</button>
				<button on:click={nextRecipe}>다음</button>
				<button on:click={deleteRecipe(recipeId)}>삭제</button>
			</div>
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

	#btnDiv {
		display: flex;
		justify-content: space-between;
	}

	:global(.main)::after {
		content: '주';
		background-color: rgb(230, 230, 255);
	}
	:global(.condiment)::after {
		content: '조';
		background-color: rgb(255, 255, 200);
	}
	:global(.spice)::after {
		content: '향';
		background-color: rgb(255, 220, 220);
	}
</style>
