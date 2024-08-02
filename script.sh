#!/bin/bash -e

# SPDX-FileCopyrightText: 2024 Rajul Jha <rajuljha49@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-only

# Prepare docker run command with arguments
docker_cmd="docker run --rm --name fossologyscanner -w /opt/repo -v ${PWD}:/opt/repo \
    -e GITHUB_TOKEN=${GITHUB_TOKEN} \
    -e GITHUB_PULL_REQUEST=${GITHUB_PULL_REQUEST} \
    -e GITHUB_REPOSITORY=${GITHUB_REPOSITORY} \
    -e GITHUB_API=${GITHUB_API_URL} \
    -e GITHUB_REPO_URL=${GITHUB_REPO_URL} \
    -e GITHUB_REPO_OWNER=${GITHUB_REPO_OWNER} \
    -e GITHUB_ACTIONS"

if [ "${KEYWORD_CONF_FILE_PATH}" != "" ]; then
    docker_cmd+=" -v ${GITHUB_WORKSPACE}/${KEYWORD_CONF_FILE_PATH}:/bin/${KEYWORD_CONF_FILE_PATH}"
fi
if [ "${ALLOWLIST_FILE_PATH}" != "" ]; then
    docker_cmd+=" -v ${GITHUB_WORKSPACE}/${ALLOWLIST_FILE_PATH}:/bin/${ALLOWLIST_FILE_PATH}"
fi
docker_cmd+=" fossology/fossology:scanner /bin/fossologyscanner"
docker_cmd+=" ${SCANNERS}"
docker_cmd+=" ${SCAN_MODE}"

# Add additional conditions
if [ "${SCAN_MODE}" == "differential" ]; then
    docker_cmd+=" --tags ${FROM_TAG} ${TO_TAG}"
fi
if [ "${KEYWORD_CONF_FILE_PATH}" != "" ]; then
    docker_cmd+=" --keyword-conf ${KEYWORD_CONF_FILE_PATH}"
fi
if [ "${ALLOWLIST_FILE_PATH}" != "" ]; then
    docker_cmd+=" --allowlist-path ${ALLOWLIST_FILE_PATH}"
fi
if [ "${REPORT_FORMAT}" != "" ]; then
    docker_cmd+=" --report ${REPORT_FORMAT}"
fi

# Run the command
echo $docker_cmd
eval $docker_cmd