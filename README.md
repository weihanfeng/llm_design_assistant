# Architecture Design Concept Generator

This repository hosts the Architecture Design Concept Generator, an application designed to aid in the creation of architectural design concepts. It leverages large language models (LLMs) to gather contextual information and uses image models to generate visual design concepts from a site image, an image mask, and a design brief.

## Features

- **Contextual Design Concepts**: Searches the web with LLMs for information relevant to the provided architectural brief and site image, ensuring generated concepts fit the context.

- **Image Mask Support**: Uses an image mask to focus design generation on specific areas of the site image.

- **Image Generation**: Transforms textual concepts into architectural design images through advanced image models.


## Getting Started

### Prerequisites

- Docker

### Installation and Usage

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/architecture-design-concept-generator.git
   ```

2. Navigate to the project directory:

3. Run the docker image
    ```sh
    docker-compose up
    ```

4. Make sure the port is correctly mapped to the host machine. The application should now be accessible at `http://localhost:8581`.

## Contributing

Contributions are welcome! If you'd like to help improve the project, please submit an issue or pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

This application streamlines the process of generating architectural design concepts by combining contextual web searches with advanced image generation, all tailored by your design brief and site specifics.