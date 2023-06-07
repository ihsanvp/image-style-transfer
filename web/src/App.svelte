<script lang="ts">
  import ImageInput from "./lib/ImageInput.svelte";
  import {ProgressBar} from "@skeletonlabs/skeleton"
  import axios from "axios"

  let generatedImgSrc = ""
  let isGenerating = false
  let taskStatus = 0  
  let socket: WebSocket
  let taskId: string | undefined
  let contentImage: File | undefined;
  let styleImage: File | undefined;

  async function generate() {
    if (contentImage && styleImage) {
      const data = new FormData()

      data.append("content_img", contentImage)
      data.append("style_img", styleImage)

      const res = await axios.post("http://localhost:8000/generate", data)
      const id = res.data.id

      if (id) {
        taskId = id
        socket = new WebSocket(`ws://localhost:8000/status/${id}`)
        socket.addEventListener("open", () => {
          isGenerating = true
        })
        socket.addEventListener("message", (e) => {
          taskStatus = e.data.completed / e.data.total
          generatedImgSrc = `http://localhost:8000/outputs/${id}.jpg?t=${new Date().getTime()}`
        })
      }
      
    }
  }
</script>

<main>
  <div
    class="container mx-auto flex flex-col items-center justify-center min-h-screen py-40"
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
        <div class="w-full h-[600px] border border-primary-800 rounded mt-12">
          {#if generatedImgSrc}
          <img class="w-full h-full object-contain" src={generatedImgSrc} alt="">
          {/if}
        </div>
        <ProgressBar max={100} value={taskStatus * 100} />
      </div>
    </div>
  </div>
</main>
