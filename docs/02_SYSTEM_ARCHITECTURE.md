# System Architecture


## Overview


Weather Engine follows a modular layered architecture where each subsystem has an independent responsibility.


The system is divided into:


1. Data Acquisition Layer

2. Storage Layer

3. Feature Engineering Layer

4. Machine Learning Inference Layer

5. Evaluation Layer

6. Presentation Layer

Open-Meteo API

        |

        v

Data Collection Engine

        |

        v

PostgreSQL Database

        |

        v

Feature Engineering

        |

        v

Hybrid Forecasting Engine

        |

        v

Prediction Storage

        |

        v

Evaluation Engine

        |

        v

Flask Dashboard + Reports

## Data Acquisition Layer


Responsible for collecting external atmospheric data.


Responsibilities:

- Fetch historical observations
- Request NWP forecast variables
- Validate incoming records
- Prevent duplicate storage


Components:

- Open-Meteo Historical API
- Open-Meteo Forecast API


## PostgreSQL Storage Layer


PostgreSQL acts as the central communication layer between independent services.


Stored entities:

- Historical observations
- NWP forecasts
- Model predictions
- Evaluation metrics
- User subscriptions


Reasons for PostgreSQL:

- ACID compliance
- Relational consistency
- Indexing support
- Python ecosystem compatibility
- Production scalability


## Machine Learning Inference Engine


The inference engine loads trained models and executes the forecasting DAG.


Responsibilities:

- Load serialized models
- Generate feature matrices
- Execute models in dependency order
- Apply hybrid consensus filtering
- Store final forecasts

