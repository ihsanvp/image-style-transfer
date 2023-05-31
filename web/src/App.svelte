<script lang="ts">
  import ImageInput from "./lib/ImageInput.svelte";

  let contentImage: File | undefined;
  let styleImage: File | undefined;

  async function generate() {
    if (contentImage && styleImage) {
      console.log(contentImage);
      console.log(styleImage);
    }
  }
</script>

<main>
  <div
    class="container mx-auto flex flex-col items-center justify-center h-screen"
  >
    <h1 class="h1 mb-28">Image Style Transfer</h1>
    <div class="grid grid-cols-6 gap-10 w-full">
      <div class="col-span-4 flex flex-col items-center justify-between">
        <div class="flex gap-10 w-full">
          <div class="flex-1">
            <ImageInput title="Content Image" bind:image={contentImage} />
          </div>
          <div class="flex-1">
            <ImageInput title="Style Image" bind:image={styleImage} />
          </div>
        </div>
        <div class="flex items-center justify-center flex-col mt-10">
          <div>
            <button
              type="button"
              class="btn variant-filled-primary px-20"
              on:click={generate}>Generate</button
            >
          </div>
        </div>
      </div>
      <div class="col-span-2">
        <div class="w-full h-[600px] border border-primary-800 rounded mt-12" />
      </div>
    </div>
  </div>
</main>
