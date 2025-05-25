from PIL import Image
from additional import *

st.set_page_config(page_title="Frequency filters", page_icon="🎨",layout="wide",
                    menu_items={"About":"Цей застосунок створено у 2025 році у межах курсової роботи"})


st.header("**Частотні фільтри**")

with open("tips.txt", 'r',encoding="utf-8") as f:
    st.sidebar.markdown(f.read())

image_file = st.file_uploader("Оберіть зображення, щоб почати:", 
                    type=["png", "jpg", "jpeg"], 
                    on_change=img_changed,
                    help="Всі результати попередніх дій буде втрачено " \
                    "щоразу, коли буде завантажено новий файл")

css='''
<style>
[data-testid="stFileUploaderDropzone"] div div::before {content:"Оберіть файл чи підтягніть його сюди"}
[data-testid="stFileUploaderDropzone"] div div span{display:none;}
[data-testid="stFileUploaderDropzone"] div div::after {color:red; font-size: .8em; content:"Ліміт: 200MB для одного файлу"}
[data-testid="stFileUploaderDropzone"] div div small{display:none;}
[data-testid="stFileUploaderDropzone"] button {visibility: hidden;}
[data-testid="stFileUploaderDropzone"] button::after {content:"Шукати файл";  visibility: visible;}
</style>
'''

st.markdown(css, unsafe_allow_html=True)

if image_file is not None:

    st.write("Оригінальна світлина:")
    st.image(image_file)
    st.divider()

    left1, right1 = st.columns(2)

    with left1:

        st.write("Чорно-біле зображення:")
        img = Image.open(image_file).convert('L')
        st.image(img)

        image_bytes = img_to_bytes(img)
        st.download_button("Завантажити чорно-біле зображення", image_bytes,
                                    file_name="grayscale_"+image_file.name, mime="image/png")

    with right1:

        if st.session_state["new"]:
            st.button("Застосувати перетворення Фур'є", on_click=apply_transform, args=(img,True))
        
        else:
            st.write("Спектр величин:")
            spectrum = spectrum_log(st.session_state["original_ft"])
            spectrum_image = Image.fromarray(spectrum).convert('L')
            st.image(spectrum_image)

            spectrum_bytes = img_to_bytes(spectrum_image)
            st.download_button("Завантажити зображення спектру", spectrum_bytes,
                file_name="spectr_"+image_file.name, mime="image/png")

    if st.session_state["original_ft"] is not None:

        st.divider()
        st.header("Налаштуйте фільтр:")
        frequency_option = st.radio( "Виберіть потрібний Вам фільтр:",
                        ["З пропуском низьких частот", "З пропуском високих частот", 
                        "Смуговий 1", "Смуговий 2"],
                        captions = ["Зміна для частот, нижчих за значення зрізу", 
                                    "Зміна для частот, вищих за значення зрізу",
                                    "Зміна для всіх частот, крім тих, що розташовані у смузі заданої ширини ( d0 - центр смуги)", 
                                    "Зміна значень частот у заданій смузі"])
        function_option = st.radio( "Виберіть потрібну функцію фільтрації:",
                        ["З ідеальним зрізом", "Гауса", 
                        "Баттерворта"])
        filter_option = function_option + " | " + frequency_option

        _min, _max, _average = d_values(st.session_state["original_ft"])

        if frequency_option == "З пропуском низьких частот" or frequency_option == "З пропуском високих частот":
            d0 = st.number_input("Задайте значення зрізу d0:",_min, _max, _average,
                        help=f"Відстань від центру спектру. Максимальне значення, що можна задати, становить {_max}, мінімальне - {_min}")
            w = None
        
        if frequency_option == "Смуговий 1" or frequency_option == "Смуговий 2" :
            d0 = st.number_input("Вкажіть значення центру смуги:",_min, _max, _average*0.5,
                        help=f"Відстань від центру спектру. Максимальне значення, що можна задати, становить {_max}, мінімальне - {_min}")
            w = st.number_input("Вкажіть ширину смуги:",_min, _max, _average*1.2)

        order = None
        if function_option == "Баттерворта":
            order = st.number_input("Вкажіть порядок для фільтра Баттерворта:", 1, 100, 2)

        st.button("Застосувати фільтр",on_click=apply_filter,args=(filter_option,d0, w, order))

        if st.session_state["filtered_ft"] is not None:

            st.divider()
            left2, right2 = st.columns(2)

            with left2:

                st.write("Спектр після фільтрації:")
                spectrum_filtered = spectrum_log(st.session_state["filtered_ft"])
                spectrum_filtered_image = Image.fromarray(spectrum_filtered).convert('L')
                st.image(spectrum_filtered_image)

                filtered_spectrum_bytes = img_to_bytes(spectrum_filtered_image)
                st.download_button("Завантажити це зображення", filtered_spectrum_bytes,
                                    file_name="filtered_spectr_"+image_file.name, mime="image/png")
            with right2:

                st.write("Світлина після зворотного перетворення:")
                transform_filtered = np.fft.ifftshift(st.session_state["filtered_ft"])
                image_filtered = np.fft.ifft2(transform_filtered)
                img_result = np.abs(image_filtered)

                image_result = Image.fromarray(img_result).convert('L')
                st.image(image_result)

                image_result_bytes = img_to_bytes(image_result)
                st.download_button("Завантажити фільтроване фото", image_result_bytes,
                                    file_name="filtered_"+image_file.name, mime="image/png")

st.divider()

# приклади
if "examples_shown" not in st.session_state:
    st.session_state["examples_shown"] = False
    st.button("Показати приклади", on_click=show_examples)
else:
    if not st.session_state["examples_shown"]:
        st.button("Показати приклади", on_click=show_examples)
    else:
        st.button("Приховати приклади", on_click=hide_examples)
        st.write("Нижче розташовано кілька прикладів застосування різноманітних фільтрів до одного зображення.")
        for example in examples_dicts:
            st.write(example["Descryption"])
            left, right = st. columns(2)
            with left:
                st.image(example["Spectrum"])
            with right:
                st.image(example["Image"])
        st.button("Згорнути приклади", on_click=hide_examples)
