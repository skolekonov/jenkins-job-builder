# Copyright 2012 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""
The Parameters module allows you to specify build parameters for a job.

**Component**: parameters
  :Macro: parameter
  :Entry Point: jenkins_jobs.parameters

Example::

  job:
    name: test_job

    parameters:
      - string:
          name: FOO
          default: bar
          description: "A parameter named FOO, defaults to 'bar'."
"""


import xml.etree.ElementTree as XML
import jenkins_jobs.modules.base


def base_param(parser, xml_parent, data, do_default, ptype):
    pdef = XML.SubElement(xml_parent, ptype)
    XML.SubElement(pdef, 'name').text = data['name']
    XML.SubElement(pdef, 'description').text = data.get('description', '')
    if do_default:
        default = data.get('default', None)
        if default:
            XML.SubElement(pdef, 'defaultValue').text = default
        else:
            XML.SubElement(pdef, 'defaultValue')
    return pdef


def string_param(parser, xml_parent, data):
    """yaml: string
    A string parameter.

    :arg str name: the name of the parameter
    :arg str default: the default value of the parameter (optional)
    :arg str description: a description of the parameter (optional)

    Example::

      parameters:
        - string:
            name: FOO
            default: bar
            description: "A parameter named FOO, defaults to 'bar'."
    """
    base_param(parser, xml_parent, data, True,
               'hudson.model.StringParameterDefinition')


def password_param(parser, xml_parent, data):
    """yaml: password
    A password parameter.

    :arg str name: the name of the parameter
    :arg str default: the default value of the parameter (optional)
    :arg str description: a description of the parameter (optional)

    Example::

      parameters:
        - password:
            name: FOO
            default: 1HSC0Ts6E161FysGf+e1xasgsHkgleLh09JUTYnipPvw=
            description: "A parameter named FOO."
    """
    base_param(parser, xml_parent, data, True,
               'hudson.model.PasswordParameterDefinition')


def bool_param(parser, xml_parent, data):
    """yaml: bool
    A boolean parameter.

    :arg str name: the name of the parameter
    :arg str default: the default value of the parameter (optional)
    :arg str description: a description of the parameter (optional)

    Example::

      parameters:
        - bool:
            name: FOO
            default: false
            description: "A parameter named FOO, defaults to 'false'."
    """
    data['default'] = str(data.get('default', False)).lower()
    base_param(parser, xml_parent, data, True,
               'hudson.model.BooleanParameterDefinition')


def file_param(parser, xml_parent, data):
    """yaml: file
    A file parameter.

    :arg str name: the target location for the file upload
    :arg str description: a description of the parameter (optional)

    Example::

      parameters:
        - file:
            name: test.txt
            description: "Upload test.txt."
    """
    base_param(parser, xml_parent, data, False,
               'hudson.model.FileParameterDefinition')


def text_param(parser, xml_parent, data):
    """yaml: text
    A text parameter.

    :arg str name: the name of the parameter
    :arg str default: the default value of the parameter (optional)
    :arg str description: a description of the parameter (optional)

    Example::

      parameters:
        - text:
            name: FOO
            default: bar
            description: "A parameter named FOO, defaults to 'bar'."
    """
    base_param(parser, xml_parent, data, True,
               'hudson.model.TextParameterDefinition')


def label_param(parser, xml_parent, data):
    """yaml: label
    A node label parameter.

    :arg str name: the name of the parameter
    :arg str default: the default value of the parameter (optional)
    :arg str description: a description of the parameter (optional)

    Example::

      parameters:
        - label:
            name: node
            default: precise
            description: "The node on which to run the job"
    """
    base_param(parser, xml_parent, data, True,
               'org.jvnet.jenkins.plugins.nodelabelparameter.'
               'LabelParameterDefinition')


def choice_param(parser, xml_parent, data):
    """yaml: choice
    A single selection parameter.

    :arg str name: the name of the parameter
    :arg list choices: the available choices
    :arg str description: a description of the parameter (optional)

    Example::

      parameters:
        - choice:
            name: project
            choices:
              - nova
              - glance
            description: "On which project to run?"
    """
    pdef = base_param(parser, xml_parent, data, False,
                      'hudson.model.ChoiceParameterDefinition')
    choices = XML.SubElement(pdef, 'choices',
                             {'class': 'java.util.Arrays$ArrayList'})
    a = XML.SubElement(choices, 'a', {'class': 'string-array'})
    for choice in data['choices']:
        XML.SubElement(a, 'string').text = choice


def node_param(parser, xml_parent, data):
    """yaml: choice
    A node parameter.
    Requires the Jenkins `NodeLabel Parameter Plugin.                             
    <https://wiki.jenkins-ci.org/display/JENKINS/                               
    NodeLabel+Parameter+Plugin>`_
 
    :arg str name: the name of the parameter
    :arg list allowed-slaves: Defines a list of nodes where 
        this job could potentially be executed on
    :arg list default-slaves: The nodes used when job gets triggered
        by anything else then manually
    :arg str trigger-condition: In case of multi node selection
        set the condition of triggering the next build on the next node
    :arg str description: a description of the parameter (optional)
    :arg str ignore-offline-nodes: Ignore nodes not online or
        not having executors (optional)

    Example::

      parameters:
        - node:
            name: srv-ubuntu
            allowed-slaves:
              - node1
              - node2
            default-slaves: 
              - node3
            trigger-condition: allow-multi-node
    """
    pdef = base_param(parser, xml_parent, data, False,
                      'org.jvnet.jenkins.plugins.'
                      'nodelabelparameter.NodeParameterDefinition')
    allowed = XML.SubElement(pdef, 'allowedSlaves')
    for slave in data['allowed-slaves']:
        XML.SubElement(allowed, 'string').text = slave
    default = XML.SubElement(pdef, 'defaultSlaves')
    for slave in data['default-slaves']:
        XML.SubElement(default, 'string').text = slave
    if data['trigger-condition'] == 'disallow-multi-node':
        XML.SubElement(pdef, 'triggerIfResult').text = \
            'multiSelectionDisallowed'
        XML.SubElement(pdef, 'allowMultiNodeSelection').text = 'false'
        XML.SubElement(pdef, 'triggerConcurrentBuilds').text = 'false'
    if data['trigger-condition'] == 'allow-multi-node':
        XML.SubElement(pdef, 'triggerIfResult').text = \
            'allowMultiSelectionForConcurrentBuilds'
        XML.SubElement(pdef, 'allowMultiNodeSelection').text = 'true'
        XML.SubElement(pdef, 'triggerConcurrentBuilds').text = 'true'
    if data['trigger-condition'] == 'success' or data['trigger-condition'] == 'unstable':
        XML.SubElement(pdef, 'triggerIfResult').text = \
            data['trigger-condition']
        XML.SubElement(pdef, 'allowMultiNodeSelection').text = 'true'
        XML.SubElement(pdef, 'triggerConcurrentBuilds').text = 'false'
    if data['trigger-condition'] == 'all-cases':
        XML.SubElement(pdef, 'triggerIfResult').text = 'allCases'
        XML.SubElement(pdef, 'allowMultiNodeSelection').text = 'true'
        XML.SubElement(pdef, 'triggerConcurrentBuilds').text = 'false'
    data['ignore-offline-nodes'] = str(
        data.get('ignore-offline-nodes', False)).lower()
    XML.SubElement(pdef, 'ignoreOfflineNodes').text = \
        data['ignore-offline-nodes']    
    

def validating_string_param(parser, xml_parent, data):
    """yaml: validating-string
    A validating string parameter
    Requires the Jenkins `Validating String Plugin.
    <https://wiki.jenkins-ci.org/display/JENKINS/
    Validating+String+Parameter+Plugin>`_

    :arg str name: the name of the parameter
    :arg str default: the default value of the parameter (optional)
    :arg str description: a description of the parameter (optional)
    :arg str regex: a regular expression to validate the string
    :arg str msg: a message to display upon failed validation

    Example::

      parameters:
        - validating-string:
            name: FOO
            default: bar
            description: "A parameter named FOO, defaults to 'bar'."
            regex: [A-Za-z]*
            msg: Your entered value failed validation
    """
    pdef = base_param(parser, xml_parent, data, True,
                      'hudson.plugins.validating__string__parameter.'
                      'ValidatingStringParameterDefinition')
    XML.SubElement(pdef, 'regex').text = data['regex']
    XML.SubElement(pdef, 'failedValidationMessage').text = data['msg']


def svn_tags_param(parser, xml_parent, data):
    """yaml: svn-tags
    A svn tag parameter
    Requires the Jenkins `Parameterized Trigger Plugin.
    <https://wiki.jenkins-ci.org/display/JENKINS/
    Parameterized+Trigger+Plugin>`_

    :arg str name: the name of the parameter
    :arg str default: the default value of the parameter (optional)
    :arg str description: a description of the parameter (optional)
    :arg str url: the url to list tags from
    :arg str filter: the regular expression to filter tags

    Example::

      parameters:
        - svn-tags:
            name: BRANCH_NAME
            default: release
            description: A parameter named BRANCH_NAME default is release
            url: http://svn.example.com/repo
            filter: [A-za-z0-9]*
    """
    pdef = base_param(parser, xml_parent, data, True,
                      'hudson.scm.listtagsparameter.'
                      'ListSubversionTagsParameterDefinition')
    XML.SubElement(pdef, 'tagsDir').text = data['url']
    XML.SubElement(pdef, 'tagsFilter').text = data.get('filter', None)
    XML.SubElement(pdef, 'reverseByDate').text = "true"
    XML.SubElement(pdef, 'reverseByName').text = "false"
    XML.SubElement(pdef, 'maxTags').text = "100"
    XML.SubElement(pdef, 'uuid').text = "1-1-1-1-1"


def dynamic_choice_param(parser, xml_parent, data):
    """yaml: dynamic-choice
    Dynamic Choice Parameter
    Requires the Jenkins `Jenkins Dynamic Parameter Plug-in.
    <https://wiki.jenkins-ci.org/display/JENKINS/
    Jenkins+Dynamic+Parameter+Plug-in>`_

    :arg str name: the name of the parameter
    :arg str description: a description of the parameter (optional)
    :arg str script: Groovy expression which generates the potential choices.
    :arg bool remote: the script will be executed on the slave where the build
        is started (default is false)
    :arg str classpath: class path for script (optional)
    :arg bool read-only: user can't modify parameter once populated
        (default is false)

    Example::

      parameters:
        - dynamic-choice:
            name: OPTIONS
            description: "Available options"
            script: "['optionA', 'optionB']"
            remote: false
            read-only: false
    """
    dynamic_param_common(parser, xml_parent, data, 'ChoiceParameterDefinition')


def dynamic_string_param(parser, xml_parent, data):
    """yaml: dynamic-string
    Dynamic Parameter
    Requires the Jenkins `Jenkins Dynamic Parameter Plug-in.
    <https://wiki.jenkins-ci.org/display/JENKINS/
    Jenkins+Dynamic+Parameter+Plug-in>`_

    :arg str name: the name of the parameter
    :arg str description: a description of the parameter (optional)
    :arg str script: Groovy expression which generates the potential choices
    :arg bool remote: the script will be executed on the slave where the build
        is started (default is false)
    :arg str classpath: class path for script (optional)
    :arg bool read-only: user can't modify parameter once populated
        (default is false)

    Example::

      parameters:
        - dynamic-string:
            name: FOO
            description: "A parameter named FOO, defaults to 'bar'."
            script: "bar"
            remote: false
            read-only: false
    """
    dynamic_param_common(parser, xml_parent, data, 'StringParameterDefinition')


def dynamic_choice_scriptler_param(parser, xml_parent, data):
    """yaml: dynamic-choice-scriptler
    Dynamic Choice Parameter (Scriptler)
    Requires the Jenkins `Jenkins Dynamic Parameter Plug-in.
    <https://wiki.jenkins-ci.org/display/JENKINS/
    Jenkins+Dynamic+Parameter+Plug-in>`_

    :arg str name: the name of the parameter
    :arg str description: a description of the parameter (optional)
    :arg str script-id: Groovy script which generates the default value
    :arg list parameters: parameters to corresponding script

        :Parameter: * **name** (`str`) Parameter name
                    * **value** (`str`) Parameter value
    :arg bool remote: the script will be executed on the slave where the build
        is started (default is false)
    :arg bool read-only: user can't modify parameter once populated
        (default is false)

    Example::

      parameters:
        - dynamic-choice-scriptler:
            name: OPTIONS
            description: "Available options"
            script-id: "scriptid.groovy"
            parameters:
              - name: param1
                value: value1
              - name: param2
                value: value2
            remote: false
            read-only: false
    """
    dynamic_scriptler_param_common(parser, xml_parent, data,
                                   'ScriptlerChoiceParameterDefinition')


def dynamic_string_scriptler_param(parser, xml_parent, data):
    """yaml: dynamic-string-scriptler
    Dynamic Parameter (Scriptler)
    Requires the Jenkins `Jenkins Dynamic Parameter Plug-in.
    <https://wiki.jenkins-ci.org/display/JENKINS/
    Jenkins+Dynamic+Parameter+Plug-in>`_

    :arg str name: the name of the parameter
    :arg str description: a description of the parameter (optional)
    :arg str script-id: Groovy script which generates the default value
    :arg list parameters: parameters to corresponding script

        :Parameter: * **name** (`str`) Parameter name
                    * **value** (`str`) Parameter value
    :arg bool remote: the script will be executed on the slave where the build
        is started (default is false)
    :arg bool read-only: user can't modify parameter once populated
        (default is false)

    Example::

      parameters:
        - dynamic-string-scriptler:
            name: FOO
            description: "A parameter named FOO, defaults to 'bar'."
            script-id: "scriptid.groovy"
            parameters:
              - name: param1
                value: value1
              - name: param2
                value: value2
            remote: false
            read-only: false
    """
    dynamic_scriptler_param_common(parser, xml_parent, data,
                                   'ScriptlerStringParameterDefinition')


def dynamic_param_common(parser, xml_parent, data, ptype):
    pdef = base_param(parser, xml_parent, data, False,
                      'com.seitenbau.jenkins.plugins.dynamicparameter.'
                      + ptype)
    XML.SubElement(pdef, '__remote').text = str(
        data.get('remote', False)).lower()
    XML.SubElement(pdef, '__script').text = data.get('script', None)
    localBaseDir = XML.SubElement(pdef, '__localBaseDirectory',
                                  {'serialization': 'custom'})
    filePath = XML.SubElement(localBaseDir, 'hudson.FilePath')
    default = XML.SubElement(filePath, 'default')
    XML.SubElement(filePath, 'boolean').text = "true"
    XML.SubElement(default, 'remote').text = \
        "/var/lib/jenkins/dynamic_parameter/classpath"
    XML.SubElement(pdef, '__remoteBaseDirectory').text = \
        "dynamic_parameter_classpath"
    XML.SubElement(pdef, '__classPath').text = data.get('classpath', None)
    XML.SubElement(pdef, 'readonlyInputField').text = str(
        data.get('read-only', False)).lower()


def dynamic_scriptler_param_common(parser, xml_parent, data, ptype):
    pdef = base_param(parser, xml_parent, data, False,
                      'com.seitenbau.jenkins.plugins.dynamicparameter.'
                      'scriptler.' + ptype)
    XML.SubElement(pdef, '__remote').text = str(
        data.get('remote', False)).lower()
    XML.SubElement(pdef, '__scriptlerScriptId').text = data.get(
        'script-id', None)
    parametersXML = XML.SubElement(pdef, '__parameters')
    parameters = data.get('parameters', [])
    if parameters:
        for parameter in parameters:
            parameterXML = XML.SubElement(parametersXML,
                                          'com.seitenbau.jenkins.plugins.'
                                          'dynamicparameter.scriptler.'
                                          'ScriptlerParameterDefinition_'
                                          '-ScriptParameter')
            XML.SubElement(parameterXML, 'name').text = parameter['name']
            XML.SubElement(parameterXML, 'value').text = parameter['value']
    XML.SubElement(pdef, 'readonlyInputField').text = str(data.get(
        'read-only', False)).lower()


class Parameters(jenkins_jobs.modules.base.Base):
    sequence = 21

    component_type = 'parameter'
    component_list_type = 'parameters'

    def gen_xml(self, parser, xml_parent, data):
        properties = xml_parent.find('properties')
        if properties is None:
            properties = XML.SubElement(xml_parent, 'properties')

        parameters = data.get('parameters', [])
        if parameters:
            pdefp = XML.SubElement(properties,
                                   'hudson.model.ParametersDefinitionProperty')
            pdefs = XML.SubElement(pdefp, 'parameterDefinitions')
            for param in parameters:
                self.registry.dispatch('parameter',
                                       parser, pdefs, param)
