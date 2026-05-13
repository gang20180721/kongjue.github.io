from flask import Flask, request, jsonify, send_file
from rembg import remove
from PIL import Image
import io
import base64

app = Flask(__name__)

@app.route('/api/remove-background', methods=['POST'])
def remove_background():
    try:
        data = request.json
        image_data = data.get('image', '')

        if not image_data:
            return jsonify({'error': 'No image provided'}), 400

        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)

        input_image = Image.open(io.BytesIO(image_bytes))

        output_image = remove(input_image)

        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{base64_image}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/composite', methods=['POST'])
def composite_image():
    try:
        data = request.json
        image_data = data.get('image', '')
        background_color = data.get('background', '#2175f3')
        size_type = data.get('size', '1inch')

        if not image_data:
            return jsonify({'error': 'No image provided'}), 400

        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)

        input_image = Image.open(io.BytesIO(image_bytes))

        output_image = remove(input_image)

        size_config = {
            '1inch': (295, 413),
            '2inch': (413, 579)
        }

        target_width, target_height = size_config.get(size_type, (295, 413))

        bg_image = Image.new('RGB', (target_width, target_height), hex_to_rgb(background_color))

        fg_width, fg_height = output_image.size
        scale = min(target_width / fg_width, target_height / fg_height)
        new_width = int(fg_width * scale)
        new_height = int(fg_height * scale)

        resized_fg = output_image.resize((new_width, new_height), Image.LANCZOS)

        offset_x = (target_width - new_width) // 2
        offset_y = (target_height - new_height) // 2

        bg_image.paste(resized_fg, (offset_x, offset_y), resized_fg)

        img_byte_arr = io.BytesIO()
        bg_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{base64_image}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)