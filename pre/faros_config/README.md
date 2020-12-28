# Faros Config

This small library is used to validate configuration provided to Project Faros. It contains the necessary parts to load a configuration from the environment, mix it with configuration from a templated YAML file, and provide a single Python object that is easy for the Inventory to work with while generating variables for hosts.

## NOTE

This library is not intended to be used outside of Project Faros, or indeed outside of the Project Faros cluster-manager container.
