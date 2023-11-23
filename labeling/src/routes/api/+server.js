export async function GET({ url }) {
    let res = await fetch(`https://www.10000recipe.com/recipe/${url.searchParams.get('id')}`);
    let data = await res.text();
    if (data.startsWith('<script>')) {
        data = null;
    } else {
        data = data.split('<div class="container">')[1].split('<!-- /contents_area -->')[0]
    }
    return new Response(data);
}