name: 🚀 Feature request
description: Suggest an idea for this project
title: "[Feature] <title>"
labels: [enhancement]
assignees: []

body:
  - type: input
    id: summary
    attributes:
      label: Feature summary
      placeholder: A concise description of your proposed feature
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation
      placeholder: Why is this feature needed? What problem does it solve?
    validations:
      required: true

  - type: textarea
    id: implementation
    attributes:
      label: Proposed implementation
      placeholder: How do you imagine this working technically?
