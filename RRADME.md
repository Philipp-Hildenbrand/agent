# 💡 TRC - Total Resource Control

## Master Your Python Projects with `trc`!

TRC (Total Resource Control) is your all-in-one Python toolkit designed to empower developers with a vast collection of practical and efficient utility functions. From streamlining routine tasks to handling complex data manipulations, `trc` helps you write cleaner, more concise, and robust code, accelerating your development workflow.

---

## 🚀 Get Started in Seconds!

Installing `trc` is a breeze. Just open your terminal and run:

```bash
pip install trc
```

---

## ✨ Why `trc`?

*   **Comprehensive Toolkit:** A single package for diverse needs – connectivity, math, file handling, string operations, and advanced data processing.
*   **Boost Productivity:** Simplify complex tasks with easy-to-use functions, letting you focus on your core logic.
*   **Clean & Efficient Code:** Write less code for more functionality, leading to better readability and maintainability.
*   **Reliable & Tested:** Robust tools built for real-world scenarios.

---

## 📚 Dive into `trc`'s Power Features

`trc` is organized into intuitive categories, ensuring you find exactly what you need, when you need it.

### 🌐 Connectivity & System Insights

Seamlessly interact with your network and gain deep insights into your system:

*   **Web Operations:** Download files and images from URLs, and check network/URL reachability.
*   **System Diagnostics:** Retrieve detailed system information including IP/MAC addresses, CPU details, RAM usage, and OS specifics.
*   **Clipboard Control:** Effortlessly copy and retrieve text from the system clipboard.

### 🔢 Mathematical Marvels

Unleash a powerful suite of mathematical functions for various computations:

*   **Prime Number Operations:** Find the Nth prime number, or quickly check if any number is prime.
*   **Sequence Generators:** Generate Fibonacci numbers and determine if a number belongs to the sequence.
*   **Number Theory Essentials:** Factorize numbers, compute Greatest Common Divisor (GCD) and Least Common Multiple (LCM), find all divisors, and identify perfect numbers.
*   **Fundamental Calculations:** Compute factorials, binomial coefficients, digit sums, and determine if a number is a power or a perfect square.
*   **Geometric Helper:** Calculate sides of a right-angled triangle using the Pythagorean theorem.

### 🗄️ File & Data Streamlining

Simplify your file management and data serialization tasks:

*   **JSON Handling:** Convert Python dictionaries to JSON files and vice-versa with ease.
*   **File Operations:** Copy files across your system efficiently.
*   **Directory Structure:** Read and represent directory structures programmatically.

### ⚡ Functional Enhancements

Elevate your Python functions with powerful decorators and execution utilities:

*   **Caching:** Boost performance by intelligently caching function results.
*   **Timing:** Accurately measure function execution times.
*   **Repetition:** Run functions multiple times for stress testing or iterative processes.
*   **Retries:** Implement robust error handling with automatic function retries on failure.

### 🔡 Variable & String Wizardry

Transform and process strings and various data types effortlessly:

*   **Text Cleaning:** Remove or retain specific characters, remove accents, and truncate text.
*   **Data Aggregation:** Merge lists or dictionaries, eliminate duplicates, and flatten nested lists.
*   **Random Generation:** Create unique random strings for various purposes.
*   **Pattern Matching:** Check for partial or complete element presence within collections.
*   **Formatting & Conversion:** Format durations, reverse objects (strings, lists), and convert text to URL-friendly slugs.
*   **Text Analysis:** Count words and characters, detect various case styles, and split text into individual words.
*   **Case Transformation:** Seamlessly convert text between `snake_case`, `kebab-case`, `PascalCase`, `camelCase`, `CONSTANT_CASE`, and `Title Case`.
*   **Palindrome Checks:** Verify if a string or sequence is a palindrome.

### 🖼️ Advanced Data & Image Processing

Specialized tools for handling images and large datasets with HDF5:

*   **Image Augmentation:** Apply a wide array of transformations to images (rotation, scaling, mirroring, blurring, noise, contrast, brightness, resizing, inversion) for data enhancement or creative effects.
*   **Image Analysis:** Calculate similarity between images and blend multiple images together.
*   **HDF5 Integration:** Efficiently read and write image and label data to and from HDF5 files, ideal for machine learning classification tasks.

### 🧠 The `trc` Agent: Your Intelligent Assistant (Total Resource Control!)

At the core of `trc`'s advanced capabilities lies its integrated AI Agent, truly embodying the "Total Resource Control" philosophy. This powerful agent is designed to interact with its environment and execute complex tasks autonomously, leveraging a diverse set of specialized tools:

*   **User Interaction (`ask_user`):** The agent can engage in a dialogue with users, asking for clarification or necessary input to proceed with tasks.
*   **File Management (`filetools`):** Comprehensive control over the file system, including reading, writing, appending, listing, creating, and deleting files and directories.
*   **System Command Execution (`shell executor`):** Ability to run arbitrary shell commands, granting the agent full control over the underlying operating system for advanced automation.
*   **Knowledge Retrieval (`wiki tool`):** Access to a vast knowledge base through Wikipedia, enabling the agent to research and gather information on demand.
*   **Multimedia Processing (`image, audio, video reader`):** Capabilities to ingest and process various multimedia formats, including images, audio, and video, for analysis or manipulation.
*   **Persistent Data Storage (`database`):** A robust internal database allows the agent to store and retrieve information for long-term memory, learning, and persistent operations.
*   **Large File & Structure Analysis (`pattern_recognizer/big_file_reader`):** Specialized tools for efficiently reading and understanding large files and complex folder structures, crucial for big data handling and deep analysis.

This intelligent agent transforms `trc` from a mere collection of utilities into a dynamic, problem-solving entity, ready to tackle challenges that require adaptive decision-making and broad operational capabilities.

---

## 🎯 Quick Usage Examples

Here's a glimpse of what you can do with `trc`:

```python
import trc
from PIL import Image

# Example 1: Download an image
try:
    img = trc.download_image("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png")
    img.save("google_logo.png")
    print("Google Logo downloaded and saved.")
except Exception as e:
    print(f"Error downloading image: {e}")

# Example 2: Get system information
sys_info = trc.sysinfo()
print(f"Operating System: {sys_info['os']}")
print(f"CPU Model: {sys_info['cpu_model']}")

# Example 3: Find the Nth prime number
prime_number = trc.nprime(7)
print(f"The 7th prime number is: {prime_number}")

# Example 4: Copy and retrieve text from clipboard
try:
    trc.clipboard_set("Hello from trc!")
    copied_text = trc.clipboard_get()
    print(f"Text from clipboard: {copied_text}")
except Exception as e:
    print(f"Error with clipboard operation: {e}")

# Example 5: Merge two lists (removing duplicates)
list1 = [1, 2, 3]
list2 = [3, 4, 5]
merged_list = trc.merge(list1, list2, duplicate=False)
print(f"Merged list (no duplicates): {merged_list}")

# Example 6: Generate a random string
random_str = trc.random_string(10)
print(f"Random string: {random_str}")

# Example 7: Slugify text
text_to_slug = "This is an Example Text for a Slug!"
slug = trc.slugify(text_to_slug)
print(f"Slug: {slug}")

# Example 8: Basic image augmentation
try:
    dummy_img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    augmented_img = trc.image_augmentation(dummy_img, rotation=45, blur=2)
    augmented_img.save("augmented_dummy_image.png")
    print("Dummy image augmented and saved.")
except Exception as e:
    print(f"Error with image augmentation: {e}")
```

---

## 👋 Contribute & Make `trc` Even Better!

We warmly welcome contributions from our community! If you discover a bug, have an idea for an improvement, or want to add an exciting new feature, please don't hesitate to:

*   Open an [issue](https://github.com/your-repo/trc/issues) to report bugs or suggest enhancements.
*   Submit a [pull request](https://github.com/your-repo/trc/pulls) with your code contributions.

Your input is invaluable in making `trc` a truly indispensable tool for everyone!

---

## 📄 License

This project is proudly licensed under the **MIT License**. For full details, please see the `LICENSE` file in the package.     wie findest du die readme