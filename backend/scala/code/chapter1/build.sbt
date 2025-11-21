ThisBuild / scalaVersion := "3.3.0"
ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "com.example"

lazy val root = (project in file("."))
  .settings(
    name := "ScalaChapter1",
    libraryDependencies += "org.scalatest" %% "scalatest" % "3.2.15" % Test
  )