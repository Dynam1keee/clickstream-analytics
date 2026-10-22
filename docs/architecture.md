# System Architecture

## Overview

The system collects clickstream events from an e-commerce website, processes them in Oracle Autonomous Data Warehouse (ADW), applies clustering with Oracle Machine Learning (OML), and presents analytical results through Oracle APEX dashboards.

## Data Flow

1. **Event collection:** JavaScript tracking captures navigation events on the e-commerce website.
2. **Data storage:** Click events are stored in the Oracle `CLICKS` table.
3. **Data processing:** SQL queries organize click events into sessions and calculate behavioral features.
4. **Behavioral analysis:** Oracle Machine Learning applies the K-Means algorithm to group sessions with similar characteristics.
5. **Visualization:** Oracle APEX dashboards display user activity, navigation patterns, and cluster characteristics.

## Main Components

| Component | Responsibility |
|---|---|
| E-commerce website | Source of navigation events |
| JavaScript tracker | Captures and submits click events |
| Python scripts | Generate synthetic clickstream data for experimentation |
| Oracle ADW | Stores and processes clickstream data |
| Oracle Machine Learning | Performs K-Means clustering |
| Oracle APEX | Visualizes analytical results |

## Data Model

The main raw-data table is `CLICKS`. Its documented columns include:

- `CLICK_ID` — unique click record identifier.
- `CLICK_TIMESTAMP` — timestamp of the event.
- `SESSION_ID` — identifier associated with the browsing session.
- `SOURCE_URL` — source page.
- `TARGET_URL` — destination page.

The processing layer derives session-level behavioral features from click events. A new sub-session can be identified when the interval between consecutive events exceeds 30 minutes.

## Current Limitations

The original Oracle environment is no longer available. This document describes the architecture implemented for the academic project; it does not imply that the entire system can currently be deployed from this repository.

Database scripts, Python code, and screenshots will be added as they are recovered and reviewed. Credentials and other sensitive connection details must not be published.

## Documentation Notes

The screenshots accompanying this documentation originate from the original academic project. Some were modified using AI-assisted image editing to translate Ukrainian text and adapt the visuals for an English-language portfolio. These modifications reduced image quality and the legibility of some text. The screenshots should therefore be treated as illustrative evidence of the project's architecture and interface rather than as exact reproductions of the original materials.