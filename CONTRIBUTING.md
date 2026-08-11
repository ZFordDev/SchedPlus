<!-- ========================================================= -->
<!-- Standards Approval Badge -->
<!-- ========================================================= -->
<table align="right">
  <tr>
    <td>
      <img src="https://raw.githubusercontent.com/ZFordDev/ZFordDev/main/assets/standards-approved.svg" width="80" alt="ZFordDev Standards Approved Badge">
    </td>
  </tr>
</table>

# Contributing to ZFordDev Projects

Thank you for your interest in contributing!  
All ZFordDev projects follow a shared set of standards designed to keep the ecosystem consistent, maintainable, and welcoming.

This document explains how to contribute code, documentation, bug reports, and feature requests across the ecosystem.

For ecosystem‑wide expectations, please read:

👉 [**STANDARDS.md**](https://github.com/ZFordDev/ZFordDev/blob/main/STANDARDS.md)  
(Clarity • Simplicity • Maintainability • Long‑term stability)

---

## Ways to Contribute

You can contribute in many ways:

- Reporting bugs  
- Suggesting new features  
- Improving documentation  
- Submitting pull requests  
- Reviewing existing issues  
- Helping refine UX or workflows  
- Testing on different platforms  

All contributions are appreciated — even small ones.

---

## Code of Conduct

By participating in this project, you agree to follow:

👉 [**CODE_OF_CONDUCT.md**](CODE_OF_CONDUCT.md)

Respect, clarity, and constructive collaboration are core values of the ecosystem.

---

## Before You Start

Please check:

- The **Issues** tab for existing reports  
- The **Roadmap** (if present)  
- The **Discussions** tab for ongoing ideas  
- The **STANDARDS.md** file for ecosystem rules  
- The **project‑specific section** below for details unique to this repository

If you’re unsure whether an idea fits, open a Discussion first — it saves everyone time.

---

## Pull Request Guidelines

To keep contributions consistent:

1. **Fork the repository**  
2. **Create a feature branch**  
   - `feature/your-feature-name`  
   - `fix/your-bug-name`
3. **Keep PRs focused**  
   - One feature or fix per PR  
   - Avoid unrelated formatting changes
4. **Follow the coding style of the project**  
   - Naming conventions  
   - File structure  
   - Module layout  
5. **Test your changes**  
   - Ensure the app builds  
   - Ensure no regressions  
6. **Write clear commit messages**  
   - Present tense  
   - Short and descriptive  
7. **Describe your PR clearly**  
   - What changed  
   - Why it changed  
   - Any side effects or considerations

Small, focused PRs are easier to review and merge.

---

## Reporting Bugs

When reporting a bug, please include:

- OS and version  
- App version  
- Steps to reproduce  
- Expected behavior  
- Actual behavior  
- Screenshots or logs (if helpful)

Clear reports help us fix issues faster.

---

## Suggesting Features

Feature requests should:

- Explain the problem, not just the solution  
- Describe the use case  
- Fit the project’s philosophy (see STANDARDS.md)  
- Avoid scope creep or IDE‑level complexity  

If unsure, open a Discussion first.

---

## Project‑Specific Guidelines

Each project may have additional rules, workflows, or architectural notes.

### SchedPlus‑Specific Notes

SchedPlus is a small, Python‑based desktop scheduler.  
Contributions should reflect its lightweight, minimal, and predictable design:

- UI changes should follow the existing layout and interaction patterns  
- Avoid introducing heavy dependencies — keep the project simple and easy to install  
- SQLite storage must remain safe, local, and predictable
- Do not add features that turn SchedPlus into a full productivity suite unless scoped and discussed  
- PyQt‑related changes should be tested on Windows and Linux when possible  
- Keep the codebase beginner‑friendly — SchedPlus is also a learning reference  
- Maintain the clean, distraction‑free feel of the interface  
- Ensure new features align with the “simple, local‑first, predictable” philosophy  
- Avoid complex background services, cloud sync, or account systems  
- Follow the existing module layout in `src/`  

---

## Thank You

Your contributions help strengthen the entire ZFordDev ecosystem.  
Whether you’re fixing a typo or building a major feature — you’re part of the project’s future.
