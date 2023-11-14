# Design

## About

This document describes the design of the program 'palvella', a web interface to command-line applications.

## Context

The 'palvella' application's purpose is to allow a user at a web browser to execute arbitrary command-line
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
  - A configuration is read from the database which tells the server what it should execute
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


#### 2. Terraform automation

Be able to automate the plan and apply steps of Terraform, with a hold step in between plan and apply.

1. User clicks UI -> run pipeline with parameters `deploy-terraform` => *true* and `environment` => *"nonprod"*
2. Pipeline "deploy-terraform" starts.
   1. Job "run-terraform-plan" runs.
      - Name: "terraform-nonprod-plan"
      - Args: `{"account": "project1", "environment":"nonprod"}`
      - Stores changed files in job storage
      - Finishes with success
   1. Job "approve-if-changed" runs
      - Requires: "terraform-nonprod-plan"
      - Previous job has no changes, so approval is skipped
      - Finishes with success
   1. Job "run-terraform-apply" runs, finishes with success
      - Name: "terraform-nonprod-apply"
      - Args: `{"account": "project1", "environment":"nonprod"}`
      - Loads changes files from job storage
      - Finishes with success
   1. Job "run-terraform-plan" runs.
      - Name: "terraform-prod-plan"
      - Args: `{"account": "project1", "environment":"prod"}`
      - Test: if pipeline.parameters.environ != "prod", then skip job
      - Loads changed files from job storage
      - Finishes with success
   1. Job "approve-if-changed" runs
      - Requires: "terraform-prod-plan"
      - Test: if pipeline.parameters.environ != "prod", then skip job
      - Previous job has changes, so hold pipeline until approval is confirmed
      - Finishes with success
   1. Job "run-terraform-apply" runs, finishes with success
      - Name: "terraform-prod-apply"
      - Args: `{"account": "project1", "environment":"prod"}`
      - Test: if pipeline.parameters.environ != "prod", then skip job
      - Finishes with success

Aspects of the job needed:
 - Ability to set name of the job
 - Ability to provide arguments to the job
 - Ability to load files from storage, or put files in storage
 - Ability to return specific job status
 - Ability to run logic to evaluate if the job should proceed

Aspects of the pipeline needed:
 - Ability to run jobs in sequence or parallel
 - Ability to 'require' a named job be completed
 - Ability to hold pipeline execution until approval is confirmed
 - Ability to skip a job in a pipeline


#### 3. Composing pipelines of applications

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


---
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


---
##### Plugins: Category: Authentication

Authentication plugins provide a means to establish the authenticity of a request.

The plugin is configured so that it can request authentication status for a particular identity.
Once the request comes back successfully, a new Authentication item is created for that identity,
which can then be used with Authorization and Permission to validate a request.

###### Plugins: Category: Authentication: Parameters
An Authentication exposes a set of methods used to determine authorization status:
 - `host`: A host to connect to in order to request authentication.

Authentication plugins expose Identity, which is a combination of metadata that can be
used later within the application to authorize requests. Some example properties of an
Identity:
 - `name`: The name of this authentication plugin. (example: "Localhost")
 - `type`: The type of this authentication plugin. (example: localhost)
 - `domain`: A logical grouping of identities.
 - `credential`: A credential to pass to the authentication system to validate.
 - `status`: Whether the identity has been successfully authenticated or not.


---
##### Plugins: Category: Authorization

Authorization plugins provide a means to determine if a component of the system is authorized
to perform a particular function. For example, if a *Credential* is configured for a specific
'authorized.role' property, only components with that role can access that credential.

Authorization plugins expose Authorizations, which are a pairing of identities and permissions.

Authorization Role properties:
 - `name`: The name of this authorization. (example: "admins")
 - `type`: The type of this authorization. (example: "rbac")
 - `identity`: The name of an identity which is authorized to do something.
 - `permission`: The name of a *Permission* which is authorized. This should be a list.


---
##### Plugins: Category: Permission

Permission plugins provide a mapping between components of the system and what those components
are allowed or not allowed to have access to.

###### Plugins: Category: Permission: object(Permission)
Permission plugins expose Permissions, which are named objects that define a group of permission
properties. Each Permission may have the following properties:
 - `identity` - The name of the authenticated identity which is requesting access. (example:
                       "mydomain/myuser-123")
 - `resource` - The name of the resource which we are controlling access for. Should be
                       a list. (examples: "job=my-job", "action=second-action", "log=action/12345",
                       "credential:name=my-ssh-key")
 - `method`   - The method that some system object wants to use, that we need to allow
                       or deny access to. Should be a list. (examples: 'credentialRead',
                       'credentialWrite', 'executorRun')
 - `effect`   - The effect that will be applied if the resource and method match on
                       what is being evaluated for permissions. (examples: "Allow", "Deny")


---
##### Plugins: Category: Credential

Credentials are objects which the app uses to provide authentication and authorization
information to different aspects of the system. They can be used to store and retrieve
user account information, connect to databases, authorize execution on a platform,
and other uses.

Credentials can receive configuration from environment variables, command-line arguments,
or by lookup in a database.

To use a Credential in configuration, you can use an object as a value for some
configuration option. The object should be like the following:
  - `from_credential`: Specifies that the value should come from the given Credential.

###### Plugins: Category: Credential: Methods
A Credential plugin uses a set of methods to access data. Example methods:
 - `add`
 - `remove`
 - `set_property`
 - `get_property`

###### Plugins: Category: Credential: Parameters
A Credential uses parameters to define how it can be used. Example properties:
 - `name`: The name of the credential. Must be unique.
 - `type`: The type of the credential. (examples: "UsermameAndPassword",
                  "Text", "SSH", "PKCS12Certificate", "Docker", "AWSECR", "Exec",
                  "GitHubOAuth", "OIDC")
 - `data`: An object which defines the contents of the Credential.


---
##### Plugins: Category: Database

Databases are the basic unit of storage of data that the app needs to operate.
It stores configuration about the app, as well as the state of Jobs within the
app, and any other configuration or state necessary for the app to run.

###### Plugins: Category: Database: Methods
A Database plugin uses a set of methods to query the database. Example methods:
 - `add`
 - `remove`
 - `connect`
 - `auth`
 - `get_property`
 - `set_property`


---
##### Plugins: Category: Job

Jobs are the basic unit of work for the app. They perform logic on a set of data
and determine the progress of the application.

A Job that calls other Jobs is called a Pipeline. This is a logical distinction;
there's nothing special about a Pipeline other than it is a series or group
of Jobs. Data is carried from one Job to another in the Pipeline.

Jobs run Actions. Actions store their state within the logical unit of a Job.

Jobs can specify a dependency on another Job.

###### Plugins: Category: Job: Parameters
Jobs can take parameters:
 - `name`: The name of the Job.
 - `engine`: The Engine to use for execution of Actions.
 - `params`: A *list of objects* of Parameters for the job. These allow you to re-use a job later
             and pass them parameters. Those parameters will show up in the job and
             any actions as 'job.self.params.<name>'. The object should look
             like this:
    - `name`: The parameter name.
    - `description`: A description of what this parameter is for.
    - `type`: The type of parameter (list, object, string, boolean)
    - `default`: The default value for this parameter.

###### Plugins: Category: Job: Methods
A Job plugin uses a set of methods to interact with the Job and its Acions.
Example methods:
 - `add`
 - `remove`
 - `run`
 - `wait`
 - `stop`
 - `set_property`
 - `get_property`


---
##### Plugins: Category: Action

Actions are the basic unit of logic executed by a Job. They perform computation
on some data, and return a status, as well as optional output.

An action can be fully specified in configuration, or it can reference a library
of actions.

Actions inherit certain configuration from Jobs:
 - `engine`: The engine to use for execution of the Action.

###### Plugins: Category: Action: Parameters
Actions can take parameters:
 - `name`: The name of the Action.
 - `type`: The type of the Action. These will be inferred in the Action if there
           exists another Parameter 

Actions can specify a dependency on another Step.

Actions can be of a couple different types:

###### Plugins: Category: Action: Type: `run`
The `run` action is configurable through a couple of different key/value options:
 - `shell`: The command and arguments used to run the shell.
 - `command`: A string which is to be executed in the shell.
 - `engine`: The *Engine* used to run commands. This can either specify an
             already configured *Engine*, or you can configure one in-line.

###### Plugins: Category: Action: Type: `approval`
The `approval` action will pause the Job until an approval is given.


###### Plugins: Category: Action: Methods
An Action plugin uses a set of methods to perform its function. Example methods:
 - `action_add`
 - `action_remove`
 - `action_run`
 - `action_wait`
 - `action_stop`
 - `action_set_property`
 - `action_get_property`


---
##### Plugins: Category: Engine

Engines are the method by which logic is executed.
They are used to execute Actions within Jobs.

While a Job specifies what we should execute, the Engine actually implements
that execution. This allows us to abstract away the platform that the execution
is performed on.

An instance of an Engine may be a process which is already running within a specific
computing environment, or it may be created dynamically at run-time as needed by
an Action or Job. An instance of an Engine when it is executing logic for an
Action or a Job is called a "Worker" (the same difference between a compiled
executable file, and a running process).


###### Plugins: Category: Engine: Parameters
Each engine takes parameters to configure it:
 - `name`: The name of the Engine.
 - `type`: The name of the 'type' of the Engine.

###### Plugins: Category: Engine: Type: `local`
The `local` engine runs commands in a shell on the same host that the *Worker* is
running in.

Parameters for this *Engine*:
 - `shell`: The shell to use to execute commands.
 - `environ`: An object of environment variables to set at execution time.

###### Plugins: Category: Engine: Type: `docker`
The `docker` engine runs commands in a Docker container.

Parameters for this *Engine*:
 - `environ`: An object of environment variables to set at execution time.
 - `volumes`: An **array of objects** specifying volumes to attach to the container at runtime.
      - `name`: The name of a directory or Docker volume.
      - `path`: The path to mount the volume in the container.

 - `context`: The name of a Docker context to use.
 - `image`: The name of the Docker image and tag to execute.
 - `platform`: The default Docker platform to use (`DOCKER_DEFAULT_PLATFORM`).
 - `http_proxy`: The `HTTP_PROXY` environment variable. Used by the Docker CLI and daemon, not by running containers.
 - `https_proxy`: The `HTTPS_PROXY` environment variable. Used by the Docker CLI and daemon, not by running containers.
 - `no_proxy`: The `NO_PROXY` environment variable. Used by the Docker CLI and daemon, not by running containers.
 - `host`: The connection method for the Docker daemon (`DOCKER_HOST`). For values see [here](https://docs.docker.com/engine/reference/commandline/cli/#a-namehosta-specify-daemon-host--h---host).
 - `config.json`: An object that specifies configuration to pass to the `config.json` file.
    - `proxies`: An object which specifies proxies to be configured in running Docker containers.
      - `default`: An object which specifies the default proxies to use in running Docker containers.
                   For values, see [here](https://docs.docker.com/engine/reference/commandline/cli/#automatic-proxy-configuration-for-containers).
 - `login`: An object with login information.
    - `username`: A username to use for Docker login.
    - `password`: A password to use for Docker login.
    - `credsStore`: The Docker [Credential Store](https://docs.docker.com/engine/reference/commandline/login/#configure-the-credential-store)
                    to use to retrieve login credentials. If this option is passed,
                    the `$HOME/.docker/config.json` file will be edited to use this option.
    - `credHelpers`: An object with credential helper information.
      - `registry` = `helpername`: Each item in this object will be added to the
                    `$HOME/.docker/config.json` file as a Docker [Credential Helper](https://docs.docker.com/engine/reference/commandline/login/#credential-helpers).
                    

###### Plugins: Category: Engine: Platforms
An Engine implements execution of logic within a "Platform". Sample platforms
include:
 - Native (execution of code within the app itself)
 - Local Exec (execution of external programs, from the same computing environment
   the app is running in)
 - Docker
 - Kubernetes
 - AWS ECS

###### Plugins: Category: Engine: Methods
An Engine uses a set of methods to perform its functions. Example methods:
 - `engine_add`
 - `engine_init`
 - `engine_run_action`
 - `engine_set_property`
 - `engine_get_property`


