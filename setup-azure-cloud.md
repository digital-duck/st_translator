# Setting up Microsoft Azure Translator Service

This guide explains how to set up the Microsoft Azure Translator service and obtain the API key and region information required for this application.

You'll need these environment variables:
*   `MS_TRANSLATOR_KEY`: Your API key for the Translator service.
*   `MS_TRANSLATOR_REGION`: The Azure region where your Translator service is deployed.
*   `MS_TRANSLATOR_ENDPOINT`: (Usually optional) The endpoint for the Translator service. The default global endpoint `https://api.cognitive.microsofttranslator.com/` is often sufficient.

Follow these steps:

1.  **Ensure you have an Azure Account.**
    *   If you don't have one, go to the [Azure portal](https://portal.azure.com/) and sign up. You might be eligible for a free account with credits.

2.  **Create a Translator Resource.**
    *   In the Azure portal, click on "+ Create a resource" or use the search bar at the top and search for "Translator".
    *   Select "Translator" from the search results (it's typically under AI + Machine Learning category).
    *   Click "Create".
    *   **Subscription**: Choose your Azure subscription.
    *   **Resource group**:
        *   You can select an existing resource group or create a new one (e.g., `translation-app-rg`). Resource groups help organize Azure resources.
    *   **Region**: Select the region where you want to deploy your Translator resource (e.g., `East US`, `West Europe`). This will be your `MS_TRANSLATOR_REGION`. **Important:** Choose a region that supports the Translator service.
    *   **Name**: Give your Translator resource a unique name (e.g., `my-translation-service`).
    *   **Pricing tier**:
        *   Choose a pricing tier. For testing and small projects, the "Free F0" tier is usually available and sufficient, allowing a certain number of characters per month for free. For production use, select an appropriate paid tier (e.g., "Standard S1").
    *   Review the terms and click "Review + create", then "Create" after validation.
    *   Wait for the deployment to complete.

3.  **Obtain API Key and Region/Endpoint.**
    *   Once the Translator resource is deployed, click on "Go to resource" or find it by searching for its name in the Azure portal.
    *   In the resource menu (left sidebar) for your Translator service, look for "Keys and Endpoint" under the "Resource Management" section.
    *   **Keys**: You will see two keys (KEY 1 and KEY 2). You can use either one. This is your `MS_TRANSLATOR_KEY`. Copy it.
    *   **Region**: The "Location" (region) is displayed here (e.g., `eastus`, `westeurope`). This is your `MS_TRANSLATOR_REGION`.
    *   **Endpoint**: The "Text Translation" endpoint is also listed (e.g., `https://api.cognitive.microsofttranslator.com/`). This is your `MS_TRANSLATOR_ENDPOINT`. For most cases, the default global endpoint used by the SDK is fine, but you can explicitly set it if needed.

4.  **Set the Environment Variables.**
    *   You need to set the `MS_TRANSLATOR_KEY` and `MS_TRANSLATOR_REGION` environment variables. `MS_TRANSLATOR_ENDPOINT` is optional if the default works for you.
        *   **For this project (using `.env` file):**
            Open your `.env` file (create one from `.env.example` if it doesn't exist) and add/update the lines:
            ```env
            MS_TRANSLATOR_KEY="<YOUR_AZURE_TRANSLATOR_API_KEY>"
            MS_TRANSLATOR_REGION="<YOUR_AZURE_REGION>"
            # MS_TRANSLATOR_ENDPOINT="https://api.cognitive.microsofttranslator.com/" # Usually not needed if using global endpoint
            ```
            Replace `<YOUR_AZURE_TRANSLATOR_API_KEY>` with the key you copied and `<YOUR_AZURE_REGION>` with your service's region (e.g., `eastus`).

**Important Security Considerations:**

*   **Treat your API keys like passwords.** They grant access to your Azure Translator service.
*   **Do not commit your API keys to your Git repository,** especially if the repository is public or shared.
*   If an API key is compromised, you can regenerate it from the "Keys and Endpoint" section in the Azure portal.

After setting the environment variables correctly (and restarting the application if it was already running), the application should be able to authenticate with the Azure Translator service.
