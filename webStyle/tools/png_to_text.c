/*
 * png_to_text.c - 将 PNG 图片转换为 ASCII 字符画
 *
 * 编译: gcc -o png_to_text png_to_text.c -lpng
 * 使用: ./png_to_text <input.png> [output.txt]
 *
 * 最大输出: 宽度 200 字符, 高度 200 字符
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <png.h>

#define MAX_WIDTH  2000
#define MAX_HEIGHT 20

// 二值化阈值（低于此值为黑色）
#define BRIGHTNESS_THRESHOLD 128
#define BLACK_CHAR '_'
#define WHITE_CHAR ' '

// 获取像素亮度 (0-255)
static int get_brightness(png_bytep *row_pointers, int x, int y, int channels) {
    png_bytep px = &(row_pointers[y][x * channels]);

    if (channels == 4 || channels == 3) {
        // RGB 转灰度: 0.299*R + 0.587*G + 0.114*B
        return (int)(px[0] * 0.299 + px[1] * 0.587 + px[2] * 0.114);
    } else if (channels == 2) {
        // 灰度 + alpha
        return px[0];
    } else {
        // 灰度
        return px[0];
    }
}

// 根据亮度选择字符（二值化：黑->'.', 白->' '）
static char brightness_to_char(int brightness) {
    return (brightness < BRIGHTNESS_THRESHOLD) ? BLACK_CHAR : WHITE_CHAR;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "用法: %s <input.png> [output.txt]\n", argv[0]);
        fprintf(stderr, "最大输出: %d x %d 字符\n", MAX_WIDTH, MAX_HEIGHT);
        return 1;
    }

    const char *input_file = argv[1];
    const char *output_file = (argc > 2) ? argv[2] : NULL;

    // 打开 PNG 文件
    FILE *fp = fopen(input_file, "rb");
    if (!fp) {
        fprintf(stderr, "错误: 无法打开文件 %s\n", input_file);
        return 1;
    }

    // 检查 PNG 签名
    png_byte header[8];
    if (fread(header, 1, 8, fp) != 8) {
        fprintf(stderr, "错误: 无法读取文件头\n");
        fclose(fp);
        return 1;
    }
    if (png_sig_cmp(header, 0, 8)) {
        fprintf(stderr, "错误: 不是有效的 PNG 文件\n");
        fclose(fp);
        return 1;
    }

    // 创建 PNG 读取结构
    png_structp png = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    if (!png) {
        fclose(fp);
        return 1;
    }

    png_infop info = png_create_info_struct(png);
    if (!info) {
        png_destroy_read_struct(&png, NULL, NULL);
        fclose(fp);
        return 1;
    }

    if (setjmp(png_jmpbuf(png))) {
        fprintf(stderr, "错误: PNG 解析失败\n");
        png_destroy_read_struct(&png, &info, NULL);
        fclose(fp);
        return 1;
    }

    png_init_io(png, fp);
    png_set_sig_bytes(png, 8);
    png_read_info(png, info);

    // 获取图片信息
    int width = png_get_image_width(png, info);
    int height = png_get_image_height(png, info);
    png_byte color_type = png_get_color_type(png, info);
    png_byte bit_depth = png_get_bit_depth(png, info);

    // 处理不同的 PNG 格式
    if (bit_depth == 16)
        png_set_strip_16(png);
    if (color_type == PNG_COLOR_TYPE_PALETTE)
        png_set_palette_to_rgb(png);
    if (color_type == PNG_COLOR_TYPE_GRAY && bit_depth < 8)
        png_set_expand_gray_1_2_4_to_8(png);
    if (png_get_valid(png, info, PNG_INFO_tRNS))
        png_set_tRNS_to_alpha(png);

    // 更新信息
    png_read_update_info(png, info);

    int channels = png_get_channels(png, info);

    // 分配内存
    png_bytep *row_pointers = (png_bytep *)malloc(sizeof(png_bytep) * height);
    for (int y = 0; y < height; y++) {
        row_pointers[y] = (png_bytep)malloc(png_get_rowbytes(png, info));
    }

    png_read_image(png, row_pointers);

    fclose(fp);

    // 计算缩放比例
    double scale_x = (double)MAX_WIDTH / width;
    double scale_y = (double)MAX_HEIGHT / height;
    double scale = (scale_x < scale_y) ? scale_x : scale_y;
    if (scale > 1.0) scale = 1.0;

    int out_width = (int)(width * scale);
    int out_height = (int)(height * scale);

    // 字符画宽高比调整 (字符约 0.5 宽)
    int char_height = (int)(out_height * 2.0);
    if (char_height > MAX_HEIGHT) char_height = MAX_HEIGHT;

    // 分配输出缓冲区
    char **output = (char **)malloc(sizeof(char *) * char_height);
    for (int y = 0; y < char_height; y++) {
        output[y] = (char *)malloc(out_width + 1);
    }

    // 转换为 ASCII
    for (int y = 0; y < char_height; y++) {
        int src_y = (int)(y / scale / 2.0);
        if (src_y >= height) src_y = height - 1;

        for (int x = 0; x < out_width; x++) {
            int src_x = (int)(x / scale);
            if (src_x >= width) src_x = width - 1;

            int brightness = get_brightness(row_pointers, src_x, src_y, channels);
            output[y][x] = brightness_to_char(brightness);
        }
        output[y][out_width] = '\0';
    }

    // 输出结果
    FILE *out = stdout;
    if (output_file) {
        out = fopen(output_file, "w");
        if (!out) {
            fprintf(stderr, "错误: 无法创建输出文件 %s\n", output_file);
            out = stdout;
        }
    }

    for (int y = 0; y < char_height; y++) {
        fprintf(out, "%s\n", output[y]);
    }

    if (out != stdout) {
        fclose(out);
        printf("已保存到 %s (%d x %d)\n", output_file, out_width, char_height);
    }

    // 释放内存
    for (int y = 0; y < height; y++) {
        free(row_pointers[y]);
    }
    free(row_pointers);

    for (int y = 0; y < char_height; y++) {
        free(output[y]);
    }
    free(output);

    png_destroy_read_struct(&png, &info, NULL);

    return 0;
}
