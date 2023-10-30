# Design

## About

This document describes the design of the program 'webrunit', a web interface to command-line applications.

## Context

The 'webrunit' application's purpose is to allow a user at a web browser to execute arbitrary command-line
applications and interact with them. The end result should be that any command-line application can have
its own web interface, so that a custom web interface does not need to be written for it.

Simply executing a command-line program and printing its output doesn't provide a lot of value for the
user. To make the output more useful, a few extra features should be implemented:

 - Convert terminal-based colors into web browser colors.
 - Allow command-line programs to output a format which can be converted into browser-friendly
   prompts, to make use of browser-based widgets and input methods.

## Design Goals

### Usage

The program should be able to be executed locally on a developer's laptop using whatever Python environment
the developer wants to use.

The program should be able to work in a modern cloud-based environment using the latest best practices,
in order to simplify operation of the application. This means running as a container with environment
variables passed to it, and optionally with volume-mounted files. Logs should be output to standard
out and standard error file descriptors.

The program's core functionality will be exposed as a library so it can be loaded by other applications
and used for whatever purpose seems fitting.

#### Usage: Use Cases

#### 1. CI platform

In order to provide the functionality of a CI platform, the following use case should be supported:

- The app starts in a K8s pod, exposing a web interface and a websocket server backend.
  Environment variables provide an instruction to connect to a database with a particular username
  and password.
  Environment variables also point to a credential for a Google Cloud service account key which is
  mounted into the filesystem at runtime.
  Environment variables also provide a Kubernetes API server and default Kubernetes service account
  credentials.

- The app enters its main waiting loop, where it reads its enviroment variables and command-line
  arguments, to determine what to do during the loop.

  - Based on the options passed (via env/cmdline args), the app loads a plugin to connect to an SQL
    database. (this plugin may be bundled with the app)
  - The app connects to an SQL database with username/password from environment variables.
  - A configuration file is read from the database which tells the server what it should execute
    during the main loop.
  - The configuration specifies that it should execute a certain configuration if it receives a
    webhook call.
  - The configuration also specifies it should execute that configuration every 10 minutes.
  - After 10 minutes, the configuration is executed:

    - The app loads a Kubernetes plugin.
    - The app creates a new Kubernetes pod to run the first Job.
      Optionally, a wrapper may be needed in the pod to start the application and monitor it,
      collecting data before/during/after its execution.
    - The app checks when the pod is finished running, and checks the exit status of the pod.
      The exit status is recorded along with any other information about the pod it might want
      to store.
    - The app evaluates the next step in the configuration to figure out what it should do next.
    - Once all steps are complete, the app should go back into its waiting loop.

#### 2. Composing pipelines of applications

- The user clicks a button in the web interface of the app that says "Create new App Pipeline".

- On a new page, the user begins crafting the pipeline.

  - The user clicks "New Job".

    - *"What type of Job?"* -> `execute container`

    - *"Enter the container registry URL:"* -> `alpine:latest`

    - *"What command and arguments should be run in the container?"* -> `cat /etc/os-release`

    - The user clicks "Action".
      - *"What name do you want to give this action?"* -> `version_match`
      - *"What type of action do you want to add to this job?"* -> `extended regular expression match on string`
      - *"What string do you want to match on?"* -> `/Alpine Linux v([0-9.]+)/`
      - *"What would you like to do on success?"* - `set job status`
        - *"What job status would you like to set?"* -> `continue job: success`
      - *"What would you like to do on failure?"* - `set job status`
        - *"What job status would you like to set?"* -> `end job: failure`

    - The user clicks "Action".
      - *"What name do you want to give this action?"* -> `version_match_success`
      - *"What type of action do you want to add to this job?"* -> `compare values`
      - *"What is the comparison you want to run?"* -> `job.current.action.version_match.output.0 == "3.18.0"`
      - *"What would you like to do on success?"* - `set job status`
        - *"What job status would you like to set?"* -> `end job: success`
      - *"What would you like to do on success?"* - `set job status`
        - *"What job status would you like to set?"* -> `continue job: success`

    - The user clicks "Action".
      - *"What name do you want to give this action?"* -> `report_error`
      - *"What type of action do you want to add to this job?"* -> `send slack message`
      - *"What slack channel would you like to send a message to?"* -> `#notifications`
      - *"What message would you like to send?"* -> `Alpine version check did not match 3.18.0`
      - No specifying of what to do at action end, so assume 'set job status -> continue job: success'.

    - The user clicks "Action".
      - *"What name do you want to give this action?"* -> `fail`
      - *"What type of action do you want to add to this job?"* -> `fail job`

    - The user clicks "Save Job".

  - Job is saved to database in a serialized format.


### Plugins

The program should use plugins to add functionality, and those plugins should be able to be installed
from a location other than the official codebase.

However, a public registry of plugins should be available, with the option to allow users to publish
a new entry in that registry. Some metadata should indicate some criteria with which to select plugins,
such as being an official plugin, or the plugin being signed by a particular public cryptographic key,
or having a certain license.

Additional private registries should be able to be added in order to completely self-host the
program while still providing the same meaningful functionality.

#### Plugins: Categories

Certain core functionality of the application should expose hooks so that plugins can hook into
that functionality.

Categories:
 - Authentication
 - Authorization
 - Permission
 - Credential
 - Database
 - Logging
 - Storage
 - Job
 - Action
 - Engine


##### Plugins: Category: Authentication

Authentication plugins provide a means to establish the authenticity of a request.

The plugin is configured so that it can request authentication status for a particular identity.
Once the request comes back successfully, a new Authentication item is created for that identity,
which can then be used with Authorization and Permission to validate a request.

An Authentication exposes a set of methods used to determine authorization status.
Example methods:
 - `config.host`: A host to connect to in order to request authentication.

Authentication plugins expose Identity, which is a combination of metadata that can be
used later within the application to authorize requests. Some example properties of an
Identity:
 - `config.name`: The name of this authentication plugin. (example: "Localhost")
 - `config.type`: The type of this authentication plugin. (example: localhost)
 - `config.domain`: A logical grouping of identities.
 - `config.credential`: A credential to pass to the authentication system to validate.
 - `status`: Whether the identity has been successfully authenticated or not.


##### Plugins: Category: Authorization

Authorization plugins provide a means to determine if a component of the system is authorized
to perform a particular function. For example, if a *Credential* is configured for a specific
'authorized.role' property, only components with that role can access that credential.

Authorization plugins expose Authorizations, which are a pairing of identities and permissions.

Authorization Role properties:
 - `config.name`: The name of this authorization. (example: "admins")
 - `config.type`: The type of this authorization. (example: "rbac")
 - `identity`: The name of an identity which is authorized to do something.
 - `permission`: The name of a *Permission* which is authorized. This should be a list.


##### Plugins: Category: Permission

Permission plugins provide a mapping between components of the system and what those components
are allowed or not allowed to have access to.

Permission plugins expose Permissions, which are named objects that define a group of permission
properties. Each Permission may have the following properties:
 - `config.identity` - The name of the authenticated identity which is requesting access. (example:
                       "mydomain/myuser-123")
 - `config.resource` - The name of the resource which we are controlling access for. Should be
                       a list. (examples: "job=my-job", "action=second-action", "log=action/12345",
                       "credential:name=my-ssh-key")
 - `config.method`   - The method that some system object wants to use, that we need to allow
                       or deny access to. Should be a list. (examples: 'credentialRead',
                       'credentialWrite', 'executorRun')
 - `config.effect`   - The effect that will be applied if the resource and method match on
                       what is being evaluated for permissions. (examples: "Allow", "Deny")


##### Plugins: Category: Credential

Credentials are objects which the app uses to provide authentication and authorization
information to different aspects of the system. They can be used to store and retrieve
user account information, connect to databases, authorize execution on a platform,
and other uses.

Credentials can receive configuration from environment variables, command-line arguments,
or by lookup in a database.

A Credential plugin uses a set of methods to access data. Example methods:
 - `add`
 - `remove`
 - `set_property`
 - `get_property`

A Credential uses properties to define how it can be used. Example properties:
 - `config.name`: The name of the credential. Must be unique.
 - `config.type`: The type of the credential. (examples: "UsermameAndPassword",
                  "Text", "SSH", "PKCS12Certificate", "Docker", "AWSECR", "Exec",
                  "GitHubOAuth", "OIDC")


##### Plugins: Category: Database

Databases are the basic unit of storage of data that the app needs to operate.
It stores configuration about the app, as well as the state of Jobs within the
app, and any other configuration or state necessary for the app to run.

A Database plugin uses a set of methods to query the database. Example methods:
 - `add`
 - `remove`
 - `connect`
 - `auth`
 - `get_property`
 - `set_property`


##### Plugins: Category: Job

Jobs are the basic unit of work for the app. They perform logic on a set of data
and determine the progress of the application.

A Job that calls other Jobs is called a Pipeline. This is a logical distinction;
there's nothing special about a Pipeline other than it is a series of Jobs, or a
group of Jobs. Data is carried from one Job to another in the Pipeline.

A Job is made up of one or more Actions. Actions store their state within the
logical unit of a Job.

A Job plugin uses a set of methods to interact with the Job and its Acions.
Example methods:
 - `add`
 - `remove`
 - `run`
 - `wait`
 - `stop`
 - `set_property`
 - `get_property`


##### Plugins: Category: Action

Actions are the basic unit of logic executed by a Job. They perform computation
on some data, and return a status, as well as optional output.

An Action plugin uses a set of methods to perform its function. Example methods:
 - `action_add`
 - `action_remove`
 - `action_run`
 - `action_wait`
 - `action_stop`
 - `action_set_property`
 - `action_get_property`


##### Plugins: Category: Engine

Engines are the basic unit of execution of logic, typically that of a Job.
While a Job specifies what we should execute, the Engine actually implements
that execution. This allows us to abstract away the platform that the execution
is performed on.

An Engine may be a process which is running within a specific computing
environment, or it may be instantiated dynamically at run-time as needed by
an Action or Job. An instance of an Engine when it is executing logic for an
Action or a Job is called a "Worker".

An Engine implements execution of logic within a "Platform". Sample platforms
include:
 - Native (execution of code within the app itself)
 - Local Exec (execution of external programs, from the same computing environment
   the app is running in)
 - Docker
 - Kubernetes
 - AWS ECS

An Engine uses a set of methods to perform its functions. Example methods:
 - `engine_add`
 - `engine_init`
 - `engine_run_action`
 - `engine_set_property`
 - `engine_get_property`

Each Engine may use whatever properties it defines in order to configure the
Engine. Some sample properties:

 - `config.name`: The name of the Engine. (example: "Docker", "Kubernetes")
 - `config.type`: The name of the 'type' of the Engine. (example: "docker")
 - `config.host`: A remote host to connect to.
 - `config.credentials`: A *Credentials* item to use as part of this platform.

