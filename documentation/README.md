# Project Documentation

This project is a Python-based API that leverages AI to automatically generate presentations from video content.

## Table of Contents

- [Project Overview](#project-overview)
- [API Documentation](./API_DOCUMENTATION.md)
- [Workflow](./WORKFLOW.md)
- [User Flow](./USER_FLOW.md)

## Project Overview

This application analyzes video content to create insightful and well-structured presentations. It works by:

1.  **Uploading and Indexing Videos**: Users can upload videos, which are then indexed for analysis by Twelve Labs.
2.  **Analyzing Video Content**: The system uses the Twelve Labs API to perform a deep analysis of the video, extracting key information such as transcripts, objects, and summaries.
3.  **Storing Analysis**: The results of the video analysis are stored in a Firebase Realtime Database for quick retrieval.
4.  **Generating Presentations**: Using the Gemini API, the application takes the stored video analysis and a user's query to generate a complete presentation in JSON format.

This powerful combination of technologies allows for the automated creation of high-quality presentations from any video content.