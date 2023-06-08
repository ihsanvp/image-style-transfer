<script lang="ts">
  import ImageInput from "./lib/ImageInput.svelte";
  import {ProgressBar, ProgressRadial} from "@skeletonlabs/skeleton"
  import axios from "axios"

  let generatedImgSrc = ""
  let isGenerating = false
  let taskTotal = 0
  let taskCompleted = 0
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
        socket.addEventListener("message", async (e) => {
          const data = JSON.parse(e.data)

          console.log(data)

          taskTotal = data.total
          taskCompleted = data.completed
          taskStatus = data.completed / data.total
          generatedImgSrc = `http://localhost:8000/outputs/${id}.jpg?t=${new Date().getTime()}`

          if (data.completed == data.total) {
            await stopGeneration()
          }
        })
      }
      
    }
  }

  async function stopGeneration() {
    socket.close()
    taskCompleted = taskTotal
    taskStatus = 1
    isGenerating = false
    await axios.post(`http://localhost:8000/stop/${taskId}`)
  }

  async function download() {
    const res = await axios.get(generatedImgSrc, {
      responseType: "blob"
    })
    const url = URL.createObjectURL(res.data)
    const a = document.createElement("a")
    a.href = url
    a.style.display = "none"
    a.download = "image-style-transfer-output.jpg"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }
</script>

<main>
  <div
    class="container mx-auto flex flex-col items-center justify-center min-h-screen py-40"
  >
    <h1 class="h1 mb-28">Image Style Transfer</h1>
    <div class="grid grid-cols-12 gap-10 w-full">
      <div class="col-span-6 flex flex-col items-center">
        <div class="flex gap-10 w-full">
          <div class="flex-1">
            <ImageInput title="Content Image" bind:image={contentImage} />
          </div>
          <div class="flex-1">
            <ImageInput title="Style Image" bind:image={styleImage} />
          </div>
        </div>
        <div class="flex items-center justify-center flex-col mt-10 gap-5">
          <div>
            <button
              type="button"
              class="btn variant-filled-primary px-20"
              disabled={isGenerating}
              on:click={generate}>
              {isGenerating ? "Generating" : "Generate"}
              </button
            >
          </div>
          {#if isGenerating}
            <div>
              <button
              type="button"
              class="btn variant-filled-error px-20"
              on:click={stopGeneration}
              >
                Stop Generation
              </button>
            </div>
          {/if}
          {#if generatedImgSrc}
          <div>
            <button
              type="button"
              class="btn variant-filled-secondary px-20"
              on:click={download}
              >
                Download
          </button>
          </div>
          {/if}
        </div>
      </div>
      <div class="col-span-6">
        <div class="h-12">
          {#if isGenerating}
            <div>
              <span>Epochs</span>
              <span>{taskCompleted}</span>
              <span>/</span>
              <span>{taskTotal}</span>
            </div>
            <div class="mb-3">
              <ProgressBar meter="bg-emerald-600" min={0} max={1} value={taskStatus} height="h-4" />
            </div>
          {/if}
        </div>
        <div class="w-full h-[600px] border border-primary-800 rounded">
          {#if generatedImgSrc}
            <img class="w-full h-full object-contain" src={generatedImgSrc} alt="">
          {:else}
            {#if isGenerating}
              <div class="flex align-center justify-center mt-52">
                <ProgressRadial stroke={50} meter="stroke-primary-500" track="stroke-primary-500/30" />
              </div>
            {/if}
          {/if}
        </div>
      </div>
    </div>
  </div>
</main>
