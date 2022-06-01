"""
Dependency:
    matplotlib scipy pillow wordcloud nltk
Provided codes were adapted from:
    http://amueller.github.io/word_cloud/
    https://github.com/hoya012/CVPR-2021-Paper-Statistics/
"""
import argparse

import matplotlib.pyplot as plt
import nltk
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_gradient_magnitude
from wordcloud import ImageColorGenerator, WordCloud

nltk.download("stopwords")
from collections import Counter

from nltk.corpus import stopwords


def get_list(args) -> list:
    with open(args.list) as f:
        papar_list = [line.strip() for line in f]
    return papar_list


def gen_keywords_fig(keyword_counter):
    # Show N most common keywords and their frequencies
    num_keyowrd = 75
    keywords_counter_vis = keyword_counter.most_common(num_keyowrd)

    plt.rcdefaults()
    _, ax = plt.subplots(figsize=(8, 18))

    key = [k[0] for k in keywords_counter_vis]
    value = [k[1] for k in keywords_counter_vis]
    y_pos = np.arange(len(key))
    ax.barh(y_pos, value, align="center", color="green", ecolor="black")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(key, rotation=0, fontsize=10)
    ax.invert_yaxis()
    for i, v in enumerate(value):
        ax.text(v + 2, i + 0.25, str(v), color="black", fontsize=10)
    ax.set_title("CVPR 2022 Submission Top {} Keywords".format(num_keyowrd))

    plt.savefig("keywords.jpg", bbox_inches="tight", dpi=128)


def gen_wordcloud_fig(keyword_list):
    # Show the word cloud forming by keywords
    parrot_color = np.array(Image.open("misc/mask.jpg"))
    # subsample by factor of 3. Very lossy but for a wordcloud we don't really care.
    parrot_color = parrot_color[::3, ::3]

    # create mask  white is "masked out"
    parrot_mask = parrot_color.copy()
    parrot_mask[parrot_mask.sum(axis=2) == 0] = 255

    # some finesse: we enforce boundaries between colors so they get less washed out.
    # For that we do some edge detection in the image
    edges = np.mean(
        [
            gaussian_gradient_magnitude(parrot_color[:, :, i] / 255.0, 2)
            for i in range(3)
        ],
        axis=0,
    )
    parrot_mask[edges > 0.08] = 255

    # create wordcloud. A bit sluggish, you can subsample more strongly for quicker rendering
    # relative_scaling=0 means the frequencies in the data are reflected less
    # acurately but it makes a better picture
    wc = WordCloud(
        max_words=1024,
        mask=parrot_mask,
        max_font_size=50,
        random_state=42,
        background_color="white",
        relative_scaling=0,
    )
    # generate word cloud
    wc.generate(" ".join(keyword_list))
    # create coloring from image
    image_colors = ImageColorGenerator(parrot_color)
    wc.recolor(color_func=image_colors)
    plt.figure(figsize=(10, 10))
    plt.imshow(wc, interpolation="bilinear")
    wc.to_file("wordcloud.png")


def run(args):
    papar_list = get_list(args)
    print(f"  == totals: {len(papar_list)}")

    stopwords_englisth = stopwords.words("english")
    stopwords_deep_learning = [
        "learning",
        "network",
        "neural",
        "networks",
        "deep",
        "via",
        "using",
        "convolutional",
        "single",
    ]

    keyword_list = []

    for idx, title in enumerate(papar_list):

        print(f"{idx} : {title}")

        word_list = title.split(" ")
        word_list = list(set(word_list))
        word_list_cleaned = []
        for word in word_list:
            word = word.lower()
            if word not in stopwords_englisth and word not in stopwords_deep_learning:
                word_list_cleaned.append(word)

        for k in range(len(word_list_cleaned)):
            keyword_list.append(word_list_cleaned[k])

    keyword_counter = Counter(keyword_list)
    print(keyword_counter)
    print(f"{len(keyword_counter)} different keywords before merging")

    # Merge duplicates: CNNs and CNN
    duplicates = []
    for k in keyword_counter:
        if k + "s" in keyword_counter:
            duplicates.append(k)
    for k in duplicates:
        keyword_counter[k] += keyword_counter[k + "s"]
        del keyword_counter[k + "s"]
    print(keyword_counter)
    print(f"{len(keyword_counter)} different keywords after merging")
    gen_keywords_fig(keyword_counter)
    gen_wordcloud_fig(keyword_list)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="CVPR 2022 Paper Statistics.")
    parser.add_argument("--list", type=str, required=True, help="Paper list")
    args = parser.parse_args()
    run(args)
