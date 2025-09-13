# API Documentation

This document provides detailed information about the API endpoints available in this project.

## Base URL

`http://localhost:3000`

---

## Endpoints

### 1. Health Check

- **GET /**

  Checks the health of the server.

  **Response (200 OK):**
  ```json
  {
    "status": "ok"
  }
  ```

### 2. Twelve Labs Health Check

- **GET /health/twelvelabs**

  Checks the status of the connection to the Twelve Labs API.

  **Response (200 OK):**
  ```json
  {
    "status": "ok"
  }
  ```

### 3. Gemini Health Check

- **GET /health/gemini**

  Checks the status of the connection to the Gemini API.

  **Response (200 OK):**
  ```json
  {
    "status": "ok"
  }
  ```

### 4. Get Indexes

- **GET /indexes**

  Retrieves a list of all available Twelve Labs indexes.

  **Response (200 OK):**
  ```json
  [
    {
      "id": "<index_id>",
      "name": "<index_name>"
    }
  ]
  ```

### 5. Get Videos in Index

- **GET /indexes/<index_id>/videos**

  Retrieves a list of all videos within a specified index.

  **Response (200 OK):**
  ```json
  [
    {
      "id": "<video_id>",
      "name": "<video_name>",
      "duration": 120.5,
      "thumbnail_url": "<url_to_thumbnail>",
      "video_url": "<url_to_video>"
    }
  ]
  ```

### 6. Upload Video

- **POST /upload**

  Uploads a new video to a specified index.

  **Request Body (multipart/form-data):**
  - `video`: The video file to upload.
  - `index_id`: The ID of the index to upload the video to.

  **Response (200 OK):**
  ```json
  {
    "status": "ready",
    "video_id": "<new_video_id>",
    "task": { ... }
  }
  ```

### 7. Analyze Video

- **POST /videos/<video_id>/analyze**

  Triggers the analysis of a video.

  **Response (200 OK):**
  - The response body will contain the detailed analysis from Twelve Labs.

### 8. Generate Presentation

- **POST /videos/<video_id>/presentation**

  Generates a presentation from the stored analysis of a video.

  **Request Body (JSON):**
  ```json
  {
    "num_slides": 5
  }
  ```

  **Response (200 OK):**
  ```json
  {
    "presentation_name": "<presentation_title>",
    "slides": [
      {
        "slide_number": 1,
        "title": "<slide_1_title>",
        "sub_points": [
          "<point_a>",
          "<point_b>"
        ]
      }
    ]
  }
  ```

### 9. Get All Presentations

- **GET /presentations**

  Retrieves a list of all generated presentations.

  **Response (200 OK):**
  ```json
  {
    "<video_id_1>": {
      "presentation_name": "<presentation_title_1>",
      "slides": [
        {
          "slide_number": 1,
          "title": "<slide_1_title>",
          "sub_points": [
            "<point_a>",
            "<point_b>"
          ]
        }
      ]
    },
    "<video_id_2>": {
      "presentation_name": "<presentation_title_2>",
      "slides": [
        {
          "slide_number": 1,
          "title": "<slide_1_title>",
          "sub_points": [
            "<point_a>",
            "<point_b>"
          ]
        }
      ]
    }
  }
  ```
