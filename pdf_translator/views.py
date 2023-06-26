from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, FileResponse
import PyPDF2
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

def split_text_by_length(text, length):
    splits = []
    while len(text) > length:
        split_index = text.rfind('.', 0, length)  # Find the last full stop within the length
        if split_index == -1:  # No full stop found within the length, split at length
            split_index = length
        splits.append(text[:split_index].strip())
        text = text[split_index:].strip()
    if text:
        splits.append(text)
    return splits


def translate_text(text, target_language):
    translator = GoogleTranslator(source='auto', target=target_language)
    translation = translator.translate(text)
    return translation



def split_pdf_text_translate(request):
    if request.method == 'POST':
        file = request.FILES['file']
        target_language = request.POST['language']

        output_directory = 'media'  # Directory to save the output files
        os.makedirs(output_directory, exist_ok=True)  # Create the output directory if it doesn't exist

        file_path = os.path.join(output_directory, file.name)
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        pdf = PyPDF2.PdfReader(open(file_path, 'rb'))
        text = ''
        num_pages = len(pdf.pages)
        for page_number in range(num_pages):
            page = pdf.pages[page_number]
            text += page.extract_text()

        splits = split_text_by_length(text, 500)
        num_splits = len(splits)
        output_texts = []
        for i, split in enumerate(splits):
            translated_text = translate_text(split, target_language)

            # Save translated text to a file
            output_file = os.path.join(output_directory, f"translated_split_{i + 1}.txt")
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(translated_text)
            output_texts.append(translated_text)

        combined_text = '\n'.join(output_texts)

        # Convert translated text to speech and save as MP3
        combined_mp3_file = os.path.join(output_directory, "translated_pdf.mp3")
        tts = gTTS(combined_text, lang=target_language)
        tts.save(combined_mp3_file)
        combined_mp3_file_relative_url = reverse('split_pdf_text_translate')
        combined_mp3_file_url = request.build_absolute_uri(combined_mp3_file_relative_url)


        return render(request, 'index.html', {
        'num_splits': num_splits,
        'combined_mp3_file': combined_mp3_file
    })

    return render(request, 'index.html')
