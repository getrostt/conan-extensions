from conan.tools.files import save
from conan.tools.cmake import CMakeDeps

import os

local_setup_bash = """\
# generated from ament_package/template/package_level/local_setup.bash.in

# source local_setup.sh from same directory as this file
_this_path=$(builtin cd "`dirname "${BASH_SOURCE[0]}"`" && pwd)
# provide AMENT_CURRENT_PREFIX to shell script
AMENT_CURRENT_PREFIX=$(builtin cd "`dirname "${BASH_SOURCE[0]}"`/../.." && pwd)
# store AMENT_CURRENT_PREFIX to restore it before each environment hook
_package_local_setup_AMENT_CURRENT_PREFIX=$AMENT_CURRENT_PREFIX

# trace output
if [ -n "$AMENT_TRACE_SETUP_FILES" ]; then
  echo "# . \\"$_this_path/local_setup.sh\\""
fi
. "$_this_path/local_setup.sh"
unset _this_path

# unset AMENT_ENVIRONMENT_HOOKS
# if not appending to them for return
if [ -z "$AMENT_RETURN_ENVIRONMENT_HOOKS" ]; then
  unset AMENT_ENVIRONMENT_HOOKS
fi

# restore AMENT_CURRENT_PREFIX before evaluating the environment hooks
AMENT_CURRENT_PREFIX=$_package_local_setup_AMENT_CURRENT_PREFIX
# list all environment hooks of this package

# source all shell-specific environment hooks of this package
# if not returning them
if [ -z "$AMENT_RETURN_ENVIRONMENT_HOOKS" ]; then
  _package_local_setup_IFS=$IFS
  IFS=":"
  for _hook in $AMENT_ENVIRONMENT_HOOKS; do
    # restore AMENT_CURRENT_PREFIX for each environment hook
    AMENT_CURRENT_PREFIX=$_package_local_setup_AMENT_CURRENT_PREFIX
    # restore IFS before sourcing other files
    IFS=$_package_local_setup_IFS
    . "$_hook"
  done
  unset _hook
  IFS=$_package_local_setup_IFS
  unset _package_local_setup_IFS
  unset AMENT_ENVIRONMENT_HOOKS
fi

unset _package_local_setup_AMENT_CURRENT_PREFIX
unset AMENT_CURRENT_PREFIX
"""

local_setup_dsv = """\
source;share/{ref_name}/environment/ament_prefix_path.sh
source;share/{ref_name}/environment/library_path.sh
source;share/{ref_name}/environment/path.sh
"""

local_setup_sh = """\
# generated from ament_package/template/package_level/local_setup.sh.in

# since this file is sourced use either the provided AMENT_CURRENT_PREFIX
# or fall back to the destination set at configure time
#: ${{AMENT_CURRENT_PREFIX:="{output_folder}/install/{ref_name}"}}
if [ ! -d "$AMENT_CURRENT_PREFIX" ]; then
  if [ -z "$COLCON_CURRENT_PREFIX" ]; then
    echo "The compile time prefix path '$AMENT_CURRENT_PREFIX' doesn't " \
      "exist. Consider sourcing a different extension than '.sh'." 1>&2
  else
    AMENT_CURRENT_PREFIX="$COLCON_CURRENT_PREFIX"
  fi
fi

# function to append values to environment variables
# using colons as separators and avoiding leading separators
ament_append_value() {{
  # arguments
  _listname="$1"
  _value="$2"
  #echo "listname $_listname"
  #eval echo "list value \$$_listname"
  #echo "value $_value"

  # avoid leading separator
  eval _values=\\"\$$_listname\\"
  if [ -z "$_values" ]; then
    eval export $_listname=\\"$_value\\"
    #eval echo "set list \$$_listname"
  else
    # field separator must not be a colon
    _ament_append_value_IFS=$IFS
    unset IFS
    eval export $_listname=\\"\$$_listname:$_value\\"
    #eval echo "append list \$$_listname"
    IFS=$_ament_append_value_IFS
    unset _ament_append_value_IFS
  fi
  unset _values

  unset _value
  unset _listname
}}

# function to append non-duplicate values to environment variables
# using colons as separators and avoiding leading separators
ament_append_unique_value() {{
  # arguments
  _listname=$1
  _value=$2
  #echo "listname $_listname"
  #eval echo "list value \$$_listname"
  #echo "value $_value"

  # check if the list contains the value
  eval _values=\$$_listname
  _duplicate=
  _ament_append_unique_value_IFS=$IFS
  IFS=":"
  if [ "$AMENT_SHELL" = "zsh" ]; then
    ament_zsh_to_array _values
  fi
  for _item in $_values; do
    # ignore empty strings
    if [ -z "$_item" ]; then
      continue
    fi
    if [ $_item = $_value ]; then
      _duplicate=1
    fi
  done
  unset _item

  # append only non-duplicates
  if [ -z "$_duplicate" ]; then
    # avoid leading separator
    if [ -z "$_values" ]; then
      eval $_listname=\\"$_value\\"
      #eval echo "set list \$$_listname"
    else
      # field separator must not be a colon
      unset IFS
      eval $_listname=\\"\$$_listname:$_value\\"
      #eval echo "append list \$$_listname"
    fi
  fi
  IFS=$_ament_append_unique_value_IFS
  unset _ament_append_unique_value_IFS
  unset _duplicate
  unset _values

  unset _value
  unset _listname
}}

# function to prepend non-duplicate values to environment variables
# using colons as separators and avoiding trailing separators
ament_prepend_unique_value() {{
  # arguments
  _listname="$1"
  _value="$2"
  #echo "listname $_listname"
  #eval echo "list value \$$_listname"
  #echo "value $_value"

  # check if the list contains the value
  eval _values=\\"\$$_listname\\"
  _duplicate=
  _ament_prepend_unique_value_IFS=$IFS
  IFS=":"
  if [ "$AMENT_SHELL" = "zsh" ]; then
    ament_zsh_to_array _values
  fi
  for _item in $_values; do
    # ignore empty strings
    if [ -z "$_item" ]; then
      continue
    fi
    if [ "$_item" = "$_value" ]; then
      _duplicate=1
    fi
  done
  unset _item

  # prepend only non-duplicates
  if [ -z "$_duplicate" ]; then
    # avoid trailing separator
    if [ -z "$_values" ]; then
      eval export $_listname=\\"$_value\\"
      #eval echo "set list \$$_listname"
    else
      # field separator must not be a colon
      unset IFS
      eval export $_listname=\\"$_value:\$$_listname\\"
      #eval echo "prepend list \$$_listname"
    fi
  fi
  IFS=$_ament_prepend_unique_value_IFS
  unset _ament_prepend_unique_value_IFS
  unset _duplicate
  unset _values

  unset _value
  unset _listname
}}

# unset AMENT_ENVIRONMENT_HOOKS
# if not appending to them for return
if [ -z "$AMENT_RETURN_ENVIRONMENT_HOOKS" ]; then
  unset AMENT_ENVIRONMENT_HOOKS
fi

# list all environment hooks of this package
ament_append_value AMENT_ENVIRONMENT_HOOKS "$AMENT_CURRENT_PREFIX/share/{ref_name}/environment/ament_prefix_path.sh"
ament_append_value AMENT_ENVIRONMENT_HOOKS "$AMENT_CURRENT_PREFIX/share/{ref_name}/environment/path.sh"

# source all shell-specific environment hooks of this package
# if not returning them
if [ -z "$AMENT_RETURN_ENVIRONMENT_HOOKS" ]; then
  _package_local_setup_IFS=$IFS
  IFS=":"
  if [ "$AMENT_SHELL" = "zsh" ]; then
    ament_zsh_to_array AMENT_ENVIRONMENT_HOOKS
  fi
  for _hook in $AMENT_ENVIRONMENT_HOOKS; do
    if [ -f "$_hook" ]; then
      # restore IFS before sourcing other files
      IFS=$_package_local_setup_IFS
      # trace output
      if [ -n "$AMENT_TRACE_SETUP_FILES" ]; then
        echo "# . \\"$_hook\\""
      fi
      . "$_hook"
    fi
  done
  unset _hook
  IFS=$_package_local_setup_IFS
  unset _package_local_setup_IFS
  unset AMENT_ENVIRONMENT_HOOKS
fi

# reset AMENT_CURRENT_PREFIX after each package
# allowing to source multiple package-level setup files
unset AMENT_CURRENT_PREFIX
"""

local_setup_zsh = """\
# generated from ament_package/template/package_level/local_setup.zsh.in

AMENT_SHELL=zsh

# source local_setup.sh from same directory as this file
_this_path=$(builtin cd -q "`dirname "${(%):-%N}"`" > /dev/null && pwd)
# provide AMENT_CURRENT_PREFIX to shell script
AMENT_CURRENT_PREFIX=$(builtin cd -q "`dirname "${(%):-%N}"`/../.." > /dev/null && pwd)
# store AMENT_CURRENT_PREFIX to restore it before each environment hook
_package_local_setup_AMENT_CURRENT_PREFIX=$AMENT_CURRENT_PREFIX

# function to convert array-like strings into arrays
# to wordaround SH_WORD_SPLIT not being set
ament_zsh_to_array() {
  local _listname=$1
  local _dollar="$"
  local _split="{="
  local _to_array="(\\"$_dollar$_split$_listname}\\")"
  eval $_listname=$_to_array
}

# trace output
if [ -n "$AMENT_TRACE_SETUP_FILES" ]; then
  echo "# . \\"$_this_path/local_setup.sh\\""
fi
# the package-level local_setup file unsets AMENT_CURRENT_PREFIX
. "$_this_path/local_setup.sh"
unset _this_path

# unset AMENT_ENVIRONMENT_HOOKS
# if not appending to them for return
if [ -z "$AMENT_RETURN_ENVIRONMENT_HOOKS" ]; then
  unset AMENT_ENVIRONMENT_HOOKS
fi

# restore AMENT_CURRENT_PREFIX before evaluating the environment hooks
AMENT_CURRENT_PREFIX=$_package_local_setup_AMENT_CURRENT_PREFIX
# list all environment hooks of this package

# source all shell-specific environment hooks of this package
# if not returning them
if [ -z "$AMENT_RETURN_ENVIRONMENT_HOOKS" ]; then
  _package_local_setup_IFS=$IFS
  IFS=":"
  for _hook in $AMENT_ENVIRONMENT_HOOKS; do
    # restore AMENT_CURRENT_PREFIX for each environment hook
    AMENT_CURRENT_PREFIX=$_package_local_setup_AMENT_CURRENT_PREFIX
    # restore IFS before sourcing other files
    IFS=$_package_local_setup_IFS
    . "$_hook"
  done
  unset _hook
  IFS=$_package_local_setup_IFS
  unset _package_local_setup_IFS
  unset AMENT_ENVIRONMENT_HOOKS
fi

unset _package_local_setup_AMENT_CURRENT_PREFIX
unset AMENT_CURRENT_PREFIX
"""

package_bash = """\
# generated from colcon_bash/shell/template/package.bash.em

# This script extends the environment for this package.

# a bash script is able to determine its own path if necessary
if [ -z "$COLCON_CURRENT_PREFIX" ]; then
  # the prefix is two levels up from the package specific share directory
  _colcon_package_bash_COLCON_CURRENT_PREFIX="$(builtin cd "`dirname "${{BASH_SOURCE[0]}}"`/../.." > /dev/null && pwd)"
else
  _colcon_package_bash_COLCON_CURRENT_PREFIX="$COLCON_CURRENT_PREFIX"
fi

# function to source another script with conditional trace output
# first argument: the path of the script
# additional arguments: arguments to the script
_colcon_package_bash_source_script() {{
  if [ -f "$1" ]; then
    if [ -n "$COLCON_TRACE" ]; then
      echo "# . \\"$1\\""
    fi
    . "$@"
  else
    echo "not found: \\"$1\\"" 1>&2
  fi
}}

# source sh script of this package
_colcon_package_bash_source_script "$_colcon_package_bash_COLCON_CURRENT_PREFIX/share/{ref_name}/package.sh"

# setting COLCON_CURRENT_PREFIX avoids determining the prefix in the sourced scripts
COLCON_CURRENT_PREFIX="$_colcon_package_bash_COLCON_CURRENT_PREFIX"

# source bash hooks
_colcon_package_bash_source_script "$COLCON_CURRENT_PREFIX/share/{ref_name}/local_setup.bash"

unset COLCON_CURRENT_PREFIX

unset _colcon_package_bash_source_script
unset _colcon_package_bash_COLCON_CURRENT_PREFIX
"""

package_dsv = """\
source;share/{ref_name}/hook/cmake_prefix_path.ps1
source;share/{ref_name}/hook/cmake_prefix_path.dsv
source;share/{ref_name}/hook/cmake_prefix_path.sh
source;share/{ref_name}/local_setup.bash
source;share/{ref_name}/local_setup.dsv
source;share/{ref_name}/local_setup.ps1
source;share/{ref_name}/local_setup.sh
source;share/{ref_name}/local_setup.zsh
"""

package_ps1 = """\
# generated from colcon_powershell/shell/template/package.ps1.em

# function to append a value to a variable
# which uses colons as separators
# duplicates as well as leading separators are avoided
# first argument: the name of the result variable
# second argument: the value to be prepended
function colcon_append_unique_value {{
  param (
    $_listname,
    $_value
  )

  # get values from variable
  if (Test-Path Env:$_listname) {{
    $_values=(Get-Item env:$_listname).Value
  }} else {{
    $_values=""
  }}
  $_duplicate=""
  # start with no values
  $_all_values=""
  # iterate over existing values in the variable
  if ($_values) {{
    $_values.Split(";") | ForEach {{
      # not an empty string
      if ($_) {{
        # not a duplicate of _value
        if ($_ -eq $_value) {{
          $_duplicate="1"
        }}
        if ($_all_values) {{
          $_all_values="${{_all_values}};$_"
        }} else {{
          $_all_values="$_"
        }}
      }}
    }}
  }}
  # append only non-duplicates
  if (!$_duplicate) {{
    # avoid leading separator
    if ($_all_values) {{
      $_all_values="${{_all_values}};${{_value}}"
    }} else {{
      $_all_values="${{_value}}"
    }}
  }}

  # export the updated variable
  Set-Item env:\$_listname -Value "$_all_values"
}}

# function to prepend a value to a variable
# which uses colons as separators
# duplicates as well as trailing separators are avoided
# first argument: the name of the result variable
# second argument: the value to be prepended
function colcon_prepend_unique_value {{
  param (
    $_listname,
    $_value
  )

  # get values from variable
  if (Test-Path Env:$_listname) {{
    $_values=(Get-Item env:$_listname).Value
  }} else {{
    $_values=""
  }}
  # start with the new value
  $_all_values="$_value"
  # iterate over existing values in the variable
  if ($_values) {{
    $_values.Split(";") | ForEach {{
      # not an empty string
      if ($_) {{
        # not a duplicate of _value
        if ($_ -ne $_value) {{
          # keep non-duplicate values
          $_all_values="${{_all_values}};$_"
        }}
      }}
    }}
  }}
  # export the updated variable
  Set-Item env:\$_listname -Value "$_all_values"
}}

# function to source another script with conditional trace output
# first argument: the path of the script
# additional arguments: arguments to the script
function colcon_package_source_powershell_script {{
  param (
    $_colcon_package_source_powershell_script
  )
  # source script with conditional trace output
  if (Test-Path $_colcon_package_source_powershell_script) {{
    if ($env:COLCON_TRACE) {{
      echo ". '$_colcon_package_source_powershell_script'"
    }}
    . "$_colcon_package_source_powershell_script"
  }} else {{
    Write-Error "not found: '$_colcon_package_source_powershell_script'"
  }}
}}


# a powershell script is able to determine its own path
# the prefix is two levels up from the package specific share directory
$env:COLCON_CURRENT_PREFIX=(Get-Item $PSCommandPath).Directory.Parent.Parent.FullName

colcon_package_source_powershell_script "$env:COLCON_CURRENT_PREFIX\share/{ref_name}/hook/cmake_prefix_path.ps1"
colcon_package_source_powershell_script "$env:COLCON_CURRENT_PREFIX\share/{ref_name}/local_setup.ps1"

Remove-Item Env:\COLCON_CURRENT_PREFIX
"""

package_sh = """\
# generated from colcon_core/shell/template/package.sh.em

# This script extends the environment for this package.

# function to prepend a value to a variable
# which uses colons as separators
# duplicates as well as trailing separators are avoided
# first argument: the name of the result variable
# second argument: the value to be prepended
_colcon_prepend_unique_value() {{
  # arguments
  _listname="$1"
  _value="$2"

  # get values from variable
  eval _values=\\"\$$_listname\\"
  # backup the field separator
  _colcon_prepend_unique_value_IFS=$IFS
  IFS=":"
  # start with the new value
  _all_values="$_value"
  # workaround SH_WORD_SPLIT not being set in zsh
  if [ "$(command -v colcon_zsh_convert_to_array)" ]; then
    colcon_zsh_convert_to_array _values
  fi
  # iterate over existing values in the variable
  for _item in $_values; do
    # ignore empty strings
    if [ -z "$_item" ]; then
      continue
    fi
    # ignore duplicates of _value
    if [ "$_item" = "$_value" ]; then
      continue
    fi
    # keep non-duplicate values
    _all_values="$_all_values:$_item"
  done
  unset _item
  # restore the field separator
  IFS=$_colcon_prepend_unique_value_IFS
  unset _colcon_prepend_unique_value_IFS
  # export the updated variable
  eval export $_listname=\\"$_all_values\\"
  unset _all_values
  unset _values

  unset _value
  unset _listname
}}

# since a plain shell script can't determine its own path when being sourced
# either use the provided COLCON_CURRENT_PREFIX
# or fall back to the build time prefix (if it exists)
_colcon_package_sh_COLCON_CURRENT_PREFIX="{output_folder}/install/{ref_name}"
if [ -z "$COLCON_CURRENT_PREFIX" ]; then
  if [ ! -d "$_colcon_package_sh_COLCON_CURRENT_PREFIX" ]; then
    echo "The build time path \\"$_colcon_package_sh_COLCON_CURRENT_PREFIX\\" doesn't exist. Either source a script for a different shell or set the environment variable \\"COLCON_CURRENT_PREFIX\\" explicitly." 1>&2
    unset _colcon_package_sh_COLCON_CURRENT_PREFIX
    return 1
  fi
  COLCON_CURRENT_PREFIX="$_colcon_package_sh_COLCON_CURRENT_PREFIX"
fi
unset _colcon_package_sh_COLCON_CURRENT_PREFIX

# function to source another script with conditional trace output
# first argument: the path of the script
# additional arguments: arguments to the script
_colcon_package_sh_source_script() {{
  if [ -f "$1" ]; then
    if [ -n "$COLCON_TRACE" ]; then
      echo "# . \\"$1\\""
    fi
    . "$@"
  else
    echo "not found: \\"$1\\"" 1>&2
  fi
}}

# source sh hooks
_colcon_package_sh_source_script "$COLCON_CURRENT_PREFIX/share/{ref_name}/hook/cmake_prefix_path.sh"
_colcon_package_sh_source_script "$COLCON_CURRENT_PREFIX/share/{ref_name}/local_setup.sh"

unset _colcon_package_sh_source_script
unset COLCON_CURRENT_PREFIX

# do not unset _colcon_prepend_unique_value since it might be used by non-primary shell hooks
"""

package_xml = """\
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>{ref_name}</name>
  <version>{ref_version}</version>
  <description>{ref_description}</description>
  <maintainer email="info@conan.io">conan</maintainer>
  <license>{ref_license}</license>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
"""

package_zsh = """\
# generated from colcon_zsh/shell/template/package.zsh.em

# This script extends the environment for this package.

# a zsh script is able to determine its own path if necessary
if [ -z "$COLCON_CURRENT_PREFIX" ]; then
  # the prefix is two levels up from the package specific share directory
  _colcon_package_zsh_COLCON_CURRENT_PREFIX="$(builtin cd -q "`dirname "${{(%):-%N}}"`/../.." > /dev/null && pwd)"
else
  _colcon_package_zsh_COLCON_CURRENT_PREFIX="$COLCON_CURRENT_PREFIX"
fi

# function to source another script with conditional trace output
# first argument: the path of the script
# additional arguments: arguments to the script
_colcon_package_zsh_source_script() {{
  if [ -f "$1" ]; then
    if [ -n "$COLCON_TRACE" ]; then
      echo "# . \\"$1\\""
    fi
    . "$@"
  else
    echo "not found: \\"$1\\"" 1>&2
  fi
}}

# function to convert array-like strings into arrays
# to workaround SH_WORD_SPLIT not being set
colcon_zsh_convert_to_array() {{
  local _listname=$1
  local _dollar="$"
  local _split="{{="
  local _to_array="(\\"$_dollar$_split$_listname}}\\")"
  eval $_listname=$_to_array
}}

# source sh script of this package
_colcon_package_zsh_source_script "$_colcon_package_zsh_COLCON_CURRENT_PREFIX/share/{ref_name}/package.sh"
unset convert_zsh_to_array

# setting COLCON_CURRENT_PREFIX avoids determining the prefix in the sourced scripts
COLCON_CURRENT_PREFIX="$_colcon_package_zsh_COLCON_CURRENT_PREFIX"

# source zsh hooks
_colcon_package_zsh_source_script "$COLCON_CURRENT_PREFIX/share/{ref_name}/local_setup.zsh"

unset COLCON_CURRENT_PREFIX

unset _colcon_package_zsh_source_script
unset _colcon_package_zsh_COLCON_CURRENT_PREFIX
"""

ament_prefix_path_dsv = """\
prepend-non-duplicate;AMENT_PREFIX_PATH;
"""

ament_prefix_path_sh = """\
# copied from
# ament_cmake_core/cmake/environment_hooks/environment/ament_prefix_path.sh

ament_prepend_unique_value AMENT_PREFIX_PATH "$AMENT_CURRENT_PREFIX"
"""

library_path_dsv = """\
prepend-non-duplicate;LD_LIBRARY_PATH;lib
"""

library_path_sh = """\
# copied from ament_package/template/environment_hook/library_path.sh

# detect if running on Darwin platform
_UNAME=`uname -s`
_IS_DARWIN=0
if [ "$_UNAME" = "Darwin" ]; then
  _IS_DARWIN=1
fi
unset _UNAME

if [ $_IS_DARWIN -eq 0 ]; then
  ament_prepend_unique_value LD_LIBRARY_PATH "$AMENT_CURRENT_PREFIX/lib"
else
  ament_prepend_unique_value DYLD_LIBRARY_PATH "$AMENT_CURRENT_PREFIX/lib"
fi
unset _IS_DARWIN
"""

path_dsv = """\
prepend-non-duplicate-if-exists;PATH;bin
"""

path_sh = """\
# copied from ament_cmake_core/cmake/environment_hooks/environment/path.sh

if [ -d "$AMENT_CURRENT_PREFIX/bin" ]; then
  ament_prepend_unique_value PATH "$AMENT_CURRENT_PREFIX/bin"
fi
"""

cmake_prefix_path_dsv = """\
prepend-non-duplicate;CMAKE_PREFIX_PATH;
"""

cmake_prefix_path_ps1 = """\
# generated from colcon_powershell/shell/template/hook_prepend_value.ps1.em

colcon_prepend_unique_value CMAKE_PREFIX_PATH "$env:COLCON_CURRENT_PREFIX"
"""

cmake_prefix_path_sh = """\
# generated from colcon_core/shell/template/hook_prepend_value.sh.em

_colcon_prepend_unique_value CMAKE_PREFIX_PATH "$COLCON_CURRENT_PREFIX"
"""

cmakelists_txt = """\
cmake_minimum_required(VERSION 3.8)
project({ref_name})

install(FILES ${{CMAKE_SOURCE_DIR}}/package.xml DESTINATION data)
"""

gitignore = """\
*
"""


class Ament(object):

    def __init__(self, conanfile):
        self.cmakedeps = CMakeDeps(conanfile)
        self._conanfile = conanfile
        self.cmakedeps_files = None

    def generate(self):
        # conan_library-consumer\install\package_dep\share\ament_index\resource_index\package_run_dependencies\package_dep : poco;ament_lint_auto;ament_lint_common
        # conan_library-consumer\install\package_dep\share\ament_index\resource_index\packages\package_dep : 
        # conan_library-consumer\install\package_dep\share\ament_index\resource_index\parent_prefix_path\package_dep : /opt/ros/humble
        # conan_library-consumer\install\package_dep\share\colcon-core\packages\package_dep : poco
        # conan_library-consumer\install\package_dep\share\package_dep\cmake\package_depConfig.cmake
        self.cmakedeps_files = self.cmakedeps.content

        for require, dep in self._conanfile.dependencies.items():
            if not require.direct:
                # Only direct depdendencies should be included
                continue
            ref_name = require.ref.name
            ament_ref_name = f"conan_{ref_name}"
            ref_version = require.ref.version
            ref_description = dep.description or "unknown"
            ref_license = dep.license or "unknown"

            self.generate_direct_dependency(ament_ref_name, ref_name, ref_version, ref_description, ref_license)
            print(f"{ref_name} dependencies:", dep.dependencies.items())
            for req, _ in dep.dependencies.items():
                self.generate_transitive_dependency(ament_ref_name, req.ref.name)
                print(f"{ref_name} dependency: ", req.ref.name)

    def generate_direct_dependency(self, ament_ref_name, ref_name, ref_version, ref_description, ref_license):
        output_folder = self._conanfile.generators_folder
        paths_content = [
            (os.path.join(ament_ref_name, "package.xml"), package_xml.format(ref_name=ament_ref_name, ref_version=ref_version, ref_description=ref_description, ref_license=ref_license)),
            (os.path.join(ament_ref_name, ".gitignore"), gitignore),
            (os.path.join(ament_ref_name, "CMakeLists.txt"), cmakelists_txt.format(ref_name=ament_ref_name)),
            (os.path.join("install", ament_ref_name, "share", "ament_index", "resource_index", "package_run_dependencies", ament_ref_name), "ament_lint_auto;ament_lint_common"),
            (os.path.join("install", ament_ref_name, "share", "ament_index", "resource_index", "packages", ament_ref_name), ""),
            (os.path.join("install", ament_ref_name, "share", "ament_index", "resource_index", "parent_prefix_path", ament_ref_name), "/opt/ros/humble"),
            (os.path.join("install", ament_ref_name, "share", "colcon-core", "packages", ament_ref_name), ""),
            (os.path.join("install", ament_ref_name, "share", ref_name, "local_setup.bash"), local_setup_bash),
            (os.path.join("install", ament_ref_name, "share", ref_name, "local_setup.dsv"), local_setup_dsv.format(ref_name=ament_ref_name)),
            (os.path.join("install", ament_ref_name, "share", ref_name, "local_setup.sh"), local_setup_sh.format(output_folder=output_folder, ref_name=ament_ref_name)),
            (os.path.join("install", ament_ref_name, "share", ref_name, "local_setup.zsh"), local_setup_zsh),
            (os.path.join("install", ament_ref_name, "share", ref_name, "package.bash"), package_bash.format(ref_name=ament_ref_name)),
            (os.path.join("install", ament_ref_name, "share", ref_name, "package.dsv"), package_dsv.format(ref_name=ament_ref_name)),
            (os.path.join("install", ament_ref_name, "share", ref_name, "package.ps1"), package_ps1.format(ref_name=ament_ref_name)),
            (os.path.join("install", ament_ref_name, "share", ref_name, "package.sh"), package_sh.format(output_folder=output_folder, ref_name=ament_ref_name)),
            (os.path.join("install", ament_ref_name, "share", ref_name, "package.xml"), package_xml.format(ref_name=ament_ref_name, ref_version=ref_version, ref_description=ref_description, ref_license=ref_license)),
            (os.path.join("install", ament_ref_name, "share", ref_name, "package.zsh"), package_zsh.format(ref_name=ament_ref_name)),
            (os.path.join("install", ament_ref_name, "share", ref_name, "environment", "ament_prefix_path.dsv"), ament_prefix_path_dsv),
            (os.path.join("install", ament_ref_name, "share", ref_name, "environment", "ament_prefix_path.sh"), ament_prefix_path_sh),
            (os.path.join("install", ament_ref_name, "share", ref_name, "environment", "library_path.dsv"), library_path_dsv),
            (os.path.join("install", ament_ref_name, "share", ref_name, "environment", "library_path.sh"), library_path_sh),
            (os.path.join("install", ament_ref_name, "share", ref_name, "environment", "path.dsv"), path_dsv),
            (os.path.join("install", ament_ref_name, "share", ref_name, "environment", "path.sh"), path_sh),
            (os.path.join("install", ament_ref_name, "share", ref_name, "hook", "cmake_prefix_path.dsv"), cmake_prefix_path_dsv),
            (os.path.join("install", ament_ref_name, "share", ref_name, "hook", "cmake_prefix_path.ps1"), cmake_prefix_path_ps1),
            (os.path.join("install", ament_ref_name, "share", ref_name, "hook", "cmake_prefix_path.sh"), cmake_prefix_path_sh),
        ]
        for path, content in paths_content:
            save(self._conanfile, path, content)

        self.generate_cmake_files(ament_ref_name, ref_name)

    def generate_cmake_files(self, ament_ref_name, require_name):
        for generator_file, content in self.cmakedeps_files.items():
            print(f"CMakeDeps generator file name: {generator_file}")
            # Create CMake files in install/<ament_ref_name>/share/<require_name>/cmake directory
            if require_name in generator_file.lower() or "cmakedeps_macros.cmake" in generator_file.lower():
              # FIXME: This is a way to save only the require_name related cmake files (and helper cmake files), however, names might not match!!
              file_path = os.path.join("install", ament_ref_name, "share", require_name, "cmake", generator_file)
              save(self._conanfile, file_path, content)

    def generate_transitive_dependency(self, ament_ref_name, require_name):
        self.generate_cmake_files(ament_ref_name, require_name)