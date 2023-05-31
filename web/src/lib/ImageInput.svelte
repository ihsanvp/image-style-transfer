<script lang="ts">
    import type { E } from "../types";
    import { FileDropzone } from "@skeletonlabs/skeleton";
    import Icon from "@iconify/svelte";

    export let title: string;
    export let image: File | undefined = undefined;

    function getPreview(file: File) {
        return URL.createObjectURL(file);
    }

    function onChange(e: E<HTMLInputElement>) {
        if (e.currentTarget.files.length) {
            image = e.currentTarget.files[0];
        }
    }

    function clear() {
        image = undefined;
    }
</script>

<div class="flex items-center justify-between">
    <h3 class="h3 mb-5">{title}</h3>
    {#if image}
        <div>
            <button
                type="button"
                class="btn-icon btn-icon-sm variant-soft-error"
                on:click={clear}
            >
                <Icon icon="mdi:close" />
            </button>
        </div>
    {/if}
</div>
<div class="h-96">
    {#if image}
        <div class="w-full h-full border border-primary-800 rounded">
            <img
                class="w-full h-full object-contain"
                src={getPreview(image)}
                alt="content_image"
            />
        </div>
    {:else}
        <FileDropzone class="h-full" name="files" on:change={onChange}>
            <svelte:fragment slot="lead">
                <div class="flex items-center justify-center">
                    <Icon icon="mdi:file-upload" class="text-4xl" />
                </div>
            </svelte:fragment>
            <svelte:fragment slot="message">
                <span class="font-bold">Upload a file</span>
                <span>or drag and drop</span>
            </svelte:fragment>
            <svelte:fragment slot="meta">
                <span class="text-center text-gray-600"
                    >PNG and JPG allowed</span
                >
            </svelte:fragment>
        </FileDropzone>
    {/if}
</div>
