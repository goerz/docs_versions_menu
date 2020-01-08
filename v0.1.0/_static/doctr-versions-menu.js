"use strict";

function getGhPagesCurrentFolder() {
  // Extract version folder under the assumpgion that the URL is of the form
  // https://<username>.github.io/<project>/<version>/...
  if (window.location.hostname.includes("github.io")){
    return window.location.pathname.split('/')[2];
  }
}

function getRootUrl() {
  // Return the "root" URL, i.e. everything before the current folder
  // (getGhPagesCurrentFolder). On gh-pages, this includes the project name.
  var root_url = window.location.origin;
  if (window.location.hostname.includes("github.io")){
    root_url = root_url + '/' + window.location.pathname.split('/')[1];
  }
  return root_url;
}

function getGithubProjectUrl(){
  // Return the project url on Github, under the assumption that the current
  // page is hosted on github-pages (https://<username>.github.io/<project>/)
  var root_url = getRootUrl();
  var match = root_url.match(/([\w\d-]+)\.github\.io\/([\w\d-]+)/)
  if (match !== null){
    var username = match[1];
    var projectname = match[2];
    return "https://github.com/" + username + "/" + projectname;
  } else {
    return null
  }
}

function _addVersionsMenu(version_data) {
  // The menu was reverse-engineered from the RTD websites, so it's very
  // specific to the sphinx_rtd_theme
  var folders = version_data["versions"];
  var root_url = getRootUrl();
  var current_url = document.URL;
  var current_folder = getGhPagesCurrentFolder();
  if (current_folder === undefined) return;
  var current_version = version_data["labels"][current_folder];
  var menu = document.createElement('div');
  menu.setAttribute('class', 'rst-versions rst-badge');
  menu.setAttribute('data-toggle', 'rst-versions');
  menu.setAttribute('role', 'note');
  menu.setAttribute('aria-label', 'versions');
  var inner_html =
    "<span class='rst-current-version' data-toggle='rst-current-version'>" +
      "<span class='fa fa-book'>  </span>" +
      "<span>" + current_version + " </span>" +
      "<span class='fa fa-caret-down'></span>" +
    "</span>" +
    "<div class='rst-other-versions'>" +
      "<div class='injected'>" +
        "<dl>" +
          "<dt>Versions</dt>";
  var i;
  for (i in folders) {
    var folder = folders[i];
    if (folder == current_folder){
      var inner_html = inner_html + "<strong><dd><a href='"
                       + current_url
                       + "'>" + current_version + "</a></dd></strong>";
    } else {
      var inner_html = inner_html + "<dd><a href='"
                       + current_url.replace(current_folder, folder)
                       + "'>" + version_data["labels"][folder] + "</a></dd>";
    }
  }
  var downloads = version_data["downloads"][current_folder];
  if (downloads.length > 0){
    var inner_html = inner_html +
          "<dt>Downloads</dt>";
    for (i in downloads) {
      var download_label = downloads[i][0];
      var download_url = downloads[i][1];
      if (!(/^(https?|ftp):/.test(download_url))){
          if (!download_url.startsWith('/')){
              var download_url = '/' + download_url;
          }
          var download_url = root_url + download_url;
      }
      var inner_html = inner_html + "<dd><a href='" + download_url + "'>"
                     + download_label + "</a></dd>";
    }
  }
  var github_project_url = getGithubProjectUrl();
  if (github_project_url !== null && github_project_url.length > 0){
    var inner_html = inner_html +
          "<dt>On Github</dt>"
          + "<dd><a href='" + github_project_url + "'>Project Home</a></dd>"
          + "<dd><a href='" + github_project_url + "/issues'>Issues</a></dd>";
  }
  var inner_html = inner_html +
        "</dl>" +
        "<hr>" +
        "<small>Generated by <a href='https://goerz.github.io/doctr_versions_menu'>Doctr Versions Menu</a>" +
        "</small>" +
      "</div>" +
    "</div>";
  menu.innerHTML = inner_html;
  var parent = document.body;
  parent.insertBefore(menu, parent.lastChild);

  // Add a warning banner for dev/outdated versions
  var warning;
  var msg;
  if (version_data["unreleased"].indexOf(current_folder) >=0){
    warning = document.createElement('div');
    warning.setAttribute('class', 'admonition danger');
    msg = "This document is for an <strong>unreleased development version</strong>.";
  }
  if (version_data["outdated"].indexOf(current_folder) >=0){
    warning = document.createElement('div');
    warning.setAttribute('class', 'admonition danger');
    msg = "This document is for an <strong>outdated version</strong>.";
  }
  if (warning !== undefined){
    if (version_data["latest_release"] !== null){
      msg = msg + " Documentation is available for the " + "<a href='" +
        current_url.replace(current_folder, version_data["latest_release"]) +
        "'>latest release</a>."
    }
    warning.innerHTML = "<p class='first admonition-title'>Note</p> " +
      "<p class='last'> " + msg + "</p>";
    var parent = document.querySelector('div.body')
      || document.querySelector('div.document')
      || document.body;
    parent.insertBefore(warning, parent.firstChild);
  }


}

function addVersionsMenu() {
  // We assume that we can load versions.json from
  // https://<username>.github.io/<project>/versions.json
  // That is, there's a <project> path between the hostname and versions.json
  var json_file = "/" + window.location.pathname.split("/")[1] + "/versions.json";
  $.getJSON(json_file, _addVersionsMenu);

  $( "body" ).on('click', "div.rst-versions.rst-badge", function() {
      $('.rst-other-versions').toggle();
      $('.rst-versions .rst-current-version .fa-book').toggleClass('shift-up');
  });
}

document.addEventListener('DOMContentLoaded', addVersionsMenu);