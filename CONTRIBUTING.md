
# Contributing to Handburger Modkit

Thank you for your interest in contributing to the Handburger Modkit! We appreciate your efforts to help improve this tool. This document outlines the steps and guidelines for contributing, specifically for adding new Python script tabs and updating the About page.

## Table of Contents

- [General Guidelines](#general-guidelines)
- [Creating a New Python Script Tab](#creating-a-new-python-script-tab)
- [Updating the About Page](#updating-the-about-page)
- [Submitting Your Contribution](#submitting-your-contribution)
- [Code of Conduct](#code-of-conduct)

## General Guidelines

1. **Follow Python Best Practices**: Ensure that your code is clean, well-documented, and adheres to Python best practices, including PEP 8 for styling.
2. **Keep Dependencies Minimal**: Avoid introducing unnecessary dependencies. If a new dependency is required, justify its inclusion and add it to the `requirements.txt` file.
3. **Testing**: Thoroughly test your script to ensure it integrates smoothly with the existing tabs and does not introduce bugs or regressions.

## Creating a New Python Script Tab

To create a new tab within the Handburger Modkit:

1. **Create Your Script**: Develop your Python script as a class that extends `QWidget` or another appropriate PyQt5 base class. The script should encapsulate its functionality and be self-contained.

2. **Tab Integration**: 
   - Place your script in the `scripts/` directory.
   - Update the `HbModkit` class in the main application to import your script.
   - Add an entry in the `add_tabs` method within `HbModkit` to include your new script as a tab. The tab should be labeled appropriately based on its functionality.

3. **Error Handling**: Implement appropriate error handling within your script to ensure that any issues do not crash the main application.

## Updating the About Page

Once your script is added, update the About page with the following steps:

1. **Modify the AboutTab Class**: 
   - Navigate to the `AboutTab` class in the main application.
   - Add a new entry to the `self.tools` dictionary that includes the name of your script and a brief description of its functionality.

2. **Ensure Proper Formatting**: The About page uses HTML for content display. Make sure your new entry is correctly formatted in HTML.

3. **Testing the Update**: After updating the About page, run the application to ensure that your new tab and its description appear correctly in the About section.

## Submitting Your Contribution

Once you’ve made your changes:

1. **Fork the Repository**: Create a fork of the repository on GitHub.
2. **Create a New Branch**: Work on your changes in a new branch named descriptively (e.g., `feature-new-tab`).
3. **Submit a Pull Request**: Once your changes are complete, submit a pull request (PR) with a clear and detailed description of what your contribution adds or modifies.
4. **Address Feedback**: Be prepared to engage in the PR review process. Address any feedback provided by maintainers to ensure your contribution meets project standards.

## Code of Conduct

We strive to maintain a welcoming and inclusive environment for all contributors. By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md), which outlines our expectations for respectful and constructive interactions.
