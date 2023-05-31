import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms.functional as F
from torchvision.utils import save_image
from torch.optim import Adam
from typing import Tuple
from PIL import Image


class VGG(nn.Module):
    def __init__(self):
        super().__init__()

        self.req_features = [0, 5, 10, 19, 28]
        self.model = models.vgg19(
            weights=models.VGG19_Weights.DEFAULT, progress=True).features[:29]  # type: ignore

    def forward(self, x):
        features = []

        for idx, layer in enumerate(self.model):
            x = layer(x)
            if idx in self.req_features:
                features.append(x)
        return features


def padded_resize(x: torch.Tensor, w: int, h: int) -> torch.Tensor:
    h_1 = x.size(1)
    w_1 = x.size(2)
    ratio_f = w / h
    ratio_1 = w_1 / h_1

    # check if the original and final aspect ratios are the same within a margin
    if round(ratio_1, 2) != round(ratio_f, 2):

        # padding to preserve aspect ratio
        hp = int(w_1/ratio_f - h_1)
        wp = int(ratio_f * h_1 - w_1)
        if hp > 0 and wp < 0:
            hp = hp // 2
            x = F.pad(x, [0, hp, 0, hp], 0, "constant")
            return F.resize(x, [h, w], antialias=True)

        elif hp < 0 and wp > 0:
            wp = wp // 2
            x = F.pad(x, [wp, 0, wp, 0], 0, "constant")
            return F.resize(x, [h, w], antialias=True)

    return F.resize(x, [h, w], antialias=True)


def unpadded_crop(x: torch.Tensor, initial_width: int, initial_height: int) -> torch.Tensor:
    w_f = x.size(2)
    h_f = x.size(1)
    ratio_f = w_f / h_f
    ratio_i = initial_width / initial_height

    if (round(ratio_i, 2)) != round(ratio_f, 2):
        if initial_width > initial_height:
            w = w_f
            h = int(h_f * (1 / ratio_i))
        else:
            h = h_f
            w = int(w_f * ratio_i)
        return F.center_crop(x, [h, w])
    return x


def open_image(path: str):
    return Image.open(path)


def load_dimension(path: str):
    img = open_image(path)
    width = img.width
    height = img.height
    img.close()
    return width, height


def load_img(path: str, device: torch.device):
    img = open_image(path)
    img = F.to_tensor(img)
    img = padded_resize(img, w=512, h=512)
    return img.to(device, torch.float)


def calc_content_loss(generated_features, content_features):
    loss = torch.mean((generated_features - content_features)**2)
    return loss


def calc_style_loss(generated_features, style_features):
    channel, height, width = generated_features.size()

    gen_view = generated_features.view(channel, width * height)
    style_view = style_features.view(channel, width * height)

    G = torch.mm(gen_view, gen_view.t())
    S = torch.mm(style_view, style_view.t())

    loss = torch.mean((G-S)**2)
    return loss


def calc_loss(generated_features, content_features, style_features, alpha: float, beta: float):
    style_loss = content_loss = 0
    # type: ignore
    for gen, og, style in list(zip(generated_features, content_features, style_features)):
        content_loss += calc_content_loss(gen, og)
        style_loss += calc_style_loss(gen, style)

    total_loss = alpha*content_loss + beta*style_loss
    return total_loss


def save_generated_image(path: str, generated: torch.Tensor, dimensions: Tuple[int, int]):
    final = generated.clone().detach().requires_grad_(False)
    final = unpadded_crop(
        final, initial_width=dimensions[0], initial_height=dimensions[1])
    save_image(final, path)


class generate_styled_image(object):
    def __init__(
        self,
        content_img_path: str,
        style_img_path: str,
        output_path: str,
        lr: float,
        epochs: int,
        alpha: float,
        beta: float,
    ):
        self.epoch = 0

        self.content_img_path = content_img_path
        self.style_img_path = style_img_path
        self.output_path = output_path
        self.lr = lr
        self.epochs = epochs
        self.alpha = alpha
        self.beta = beta

        self.initialize()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def initialize(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.image_size = load_dimension(self.content_img_path)

        self.content_image = load_img(
            self.content_img_path, device=self.device)
        self.style_image = load_img(
            self.style_img_path, device=self.device)
        self.generated_image = self.content_image.clone().requires_grad_(True)

        self.model = VGG().to(self.device).eval()
        self.optimizer = Adam([self.generated_image], lr=self.lr)

    def next(self):
        if self.epoch < self.epochs:
            self.epoch += 1

            generated_features = self.model(self.generated_image)
            content_features = self.model(self.content_image)
            style_features = self.model(self.style_image)

            total_loss = calc_loss(
                generated_features,
                content_features,
                style_features,
                alpha=self.alpha,
                beta=self.beta,
            )

            self.optimizer.zero_grad()
            total_loss.backward()  # type: ignore
            self.optimizer.step()

            return self.epoch

        raise StopIteration()
