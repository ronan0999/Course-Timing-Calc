<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xy="http://xyleme.com/xylink">
  <xsl:output method="html" version="5" encoding="UTF-8" indent="no" />
  <xsl:strip-space elements="*" />

  <xsl:template match="//Slide">
    <div class="slide">
        <ul>
            <li>Theme: <xsl:value-of select="./@slideTheme"/></li>
            <li>Slide Elements: (<xsl:value-of select="count(./*)"/>)</li>
            <li>Body Elements: (<xsl:value-of select="count(./Body/*)"/>)</li>
        </ul>
        <xsl:apply-templates select=".//Title"/>
        <xsl:choose>
            <xsl:when test="@slideTheme = 'TitleSlide'">
                <xsl:apply-templates select=".//Body" mode="TitleSlide"/>
            </xsl:when>
            <xsl:when test="@slideTheme = 'SingleContent'">
                <xsl:apply-templates select=".//Body" mode="SingleContent"/>
            </xsl:when>
            <xsl:when test="@slideTheme = 'SideBySide'">
                <xsl:apply-templates select=".//Body" mode="SideBySide"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates select=".//Body"/>
            </xsl:otherwise>
        </xsl:choose>
        
        <xsl:apply-templates select=".//SlideNote"/>
    </div>
  </xsl:template>

  <xsl:template match="//Slide/Title">
    <h1 class="slide-title"><xsl:apply-templates/></h1>
  </xsl:template>

  <xsl:template match="//Body">
    <div class="slide-body slide-tpl-content">
        <div class="slide-tpl-content-container">
            <xsl:for-each select="./*">
                <div style="flex: 1"><xsl:apply-templates select="."/></div>
            </xsl:for-each>
        </div>
    </div>
  </xsl:template>

  <xsl:template match="//Slide/SlideNote">
    <div class="slide-note">Note<xsl:apply-templates/></div>
  </xsl:template>

  <!-- Slide Themes -->

  <xsl:template match="//Body" mode="TitleSlide">
    <div class="slide-body slide-tpl-content">
        <div class="slide-tpl-content-container">
            TITLE SLIDE
            <xsl:for-each select="./*">
                <div style="flex: 1"><xsl:apply-templates/></div>
            </xsl:for-each>
        </div>
    </div>
  </xsl:template>

  <xsl:template match="//Body" mode="SingleContent">
    <div class="slide-body slide-tpl-content">
        <div class="slide-tpl-content-container">
            <xsl:for-each select="./*">
                <div><xsl:apply-templates/></div>
            </xsl:for-each>
        </div>
    </div>
  </xsl:template>

  <xsl:template match="//Body" mode="SideBySide">
    <div class="slide-body slide-tpl-content">
        <div class="slide-tpl-content-container slide-flex">
            <xsl:for-each select="./*">
                <div style="flex: 1"><xsl:apply-templates/></div>
            </xsl:for-each>
        </div>
    </div>
  </xsl:template>

  <xsl:template match="//Body">
    <div class="slide-body slide-tpl-content">
        <div class="slide-tpl-content-container">
            <xsl:for-each select="./*">
                <div style="flex: 1"><xsl:apply-templates select="."/></div>
            </xsl:for-each>
        </div>
    </div>
  </xsl:template>

  <!-- Universal Matchers -->

  <xsl:template match="//Icon">
    <div class="icon">
      <xsl:element name="img">
        <xsl:attribute name="src">
          <xsl:value-of select="translate(@uri, ' ', '_')"/>
        </xsl:attribute>
        <xsl:attribute name="width">
          <xsl:value-of select="@thumbWidth"/>
        </xsl:attribute>
      </xsl:element>
    </div>
  </xsl:template>

  <xsl:template match="//RichText">
    <div class="richtext"><xsl:apply-templates/></div>
  </xsl:template>

  <!-- <xsl:template match="//RichText/text()" name="insertBreaks">
    <xsl:param name="para-text" select="."/>

    <xsl:choose>
      <xsl:when test="not(contains($para-text, '&#xA;&#xA;'))">
        <xsl:copy-of select="$para-text"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="substring-before($para-text, '&#xA;&#xA;')"/>
        <br/>
        <br/>
        <xsl:call-template name="insertBreaks">
          <xsl:with-param name="para-text" select=
            "substring-after($para-text, '&#xA;&#xA;')"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template> -->

  <xsl:template match="//Emph">
    <strong><xsl:apply-templates/></strong>
  </xsl:template>

  <xsl:template match="//Italic">
    <em><xsl:apply-templates/></em>
  </xsl:template>

  <xsl:template match="//Code">
    <pre><code><xsl:apply-templates/></code></pre>
  </xsl:template>

  <xsl:template match="//InLineCode">
    <code><xsl:apply-templates/></code>
  </xsl:template>

  <xsl:template match="//InLineTypeThis">
    <code><xsl:apply-templates/></code>
  </xsl:template>

  <xsl:template match="//InLineApplicationPrompt">
    <code><xsl:apply-templates/></code>
  </xsl:template>

  <xsl:template match="//InLineMenuSelection">
    <code><xsl:apply-templates/></code>
  </xsl:template>

  <xsl:template match="//Footnote">
    <xsl:element name="a">
      <xsl:attribute name="href">#footnote-<xsl:number level="any" count="Footnote" format="1"/></xsl:attribute>
      <xsl:attribute name="class">footnote-anchor</xsl:attribute>
      <xsl:number level="any" count="Footnote" format="[1]"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="//Href">
    <xsl:element name="a">
      <xsl:attribute name="href"><xsl:value-of select="@UrlTarget"/></xsl:attribute>
      <xsl:value-of select="text()"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="//Xref">
    <xsl:element name="a">
      <xsl:attribute name="href">#ref-<xsl:value-of select="@InsideTargetRef"/></xsl:attribute>
      <xsl:value-of select="text()"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="//FilterMetadata">
  </xsl:template>


  <xsl:template match="//Tabs">
    <div class="tabs">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="//Tab">
    <div class="tab"><xsl:apply-templates/></div>
  </xsl:template>

  <xsl:template match="//Tab/Label">
    <p class="bold"><xsl:apply-templates/></p>
  </xsl:template>

  <xsl:template match="//Tab/Content">
    <div class="tab-content"><xsl:apply-templates/></div>
  </xsl:template>

  <xsl:template match="//InLineMenuSelection">
    <code><xsl:apply-templates/></code>
  </xsl:template>

  <xsl:template match="//List">
    <xsl:apply-templates select="./ListPreamble"/>
    <xsl:variable name="list_marker" select="@ListMarker"/>
    <xsl:choose>
      <xsl:when test="$list_marker = 'Numeric'">
        <ul class="number-list"><xsl:apply-templates select="./ItemBlock"/></ul>
      </xsl:when>
      <xsl:otherwise>
        <ul class="bullet-list"><xsl:apply-templates select="./ItemBlock"/></ul>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="//ListPreamble">
    <div class="list-preamble"><xsl:apply-templates/></div>
  </xsl:template>

  <xsl:template match="//Item">
    <li class="item"><xsl:apply-templates/></li>
  </xsl:template>

  <xsl:template match="//ItemPara">
    <div class="item-para"><xsl:apply-templates/></div>
  </xsl:template>

  <xsl:template match="//List//Item//SubList">
    <xsl:element name="ul">
      <xsl:attribute name="class"><xsl:value-of select="@ListMarker"/></xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>


  <!-- Composite Matchers -->


  <xsl:template match="//Table">
    <div class="">
      <table border="1">
        <!-- <xsl:apply-templates select="/TblTitle"/>
        <xsl:apply-templates select="/TblGroup"/> -->
        <xsl:apply-templates/>
      </table>
    </div>
  </xsl:template>

  <xsl:template match="//TblBody">
    <tbody><xsl:apply-templates/></tbody>
  </xsl:template>

  <xsl:template match="//TblHeader">
    <thead><xsl:apply-templates/></thead>
  </xsl:template>

  <xsl:template match="//TableRow">
    <tr><xsl:apply-templates/></tr>
  </xsl:template>

  <xsl:template match="//Cell">
    <td><xsl:apply-templates/></td>
  </xsl:template>

  <!-- <xsl:template match="//Table//TblHeader/TableRow/Cell">
    <xsl:variable name="rowspan" select="@rowspan"/>
    <xsl:element name="th">
      <xsl:attribute name="rowspan">
        <xsl:value-of select="$rowspan">
        </xsl:value-of>
      </xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="//Table/TblGroup[TblHeader[string-length() = 0]]/TblBody//TableRow[position() = 1]/Cell">
    <xsl:variable name="rowspan" select="@rowspan"/>

    <xsl:element name="th">
      <xsl:attribute name="rowspan">
        <xsl:value-of select="$rowspan">
        </xsl:value-of>
      </xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="//Table/TblGroup[TblHeader[string-length() = 0]]/TblBody//TableRow[position() != 1]/Cell">
    <xsl:variable name="rowspan" select="@rowspan"/>

    <xsl:element name="td">
      <xsl:attribute name="rowspan">
        <xsl:value-of select="$rowspan">
        </xsl:value-of>
      </xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="//Table/TblGroup[TblHeader[string-length() != 0]]/TblBody//TableRow/Cell">
    <xsl:variable name="rowspan" select="@rowspan"/>
    <xsl:element name="td">
      <xsl:attribute name="rowspan">
        <xsl:value-of select="$rowspan">
        </xsl:value-of>
      </xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template> -->

  <xsl:template match="/IA/CoverPage/Title">
      <title><xsl:apply-templates/></title>
  </xsl:template>

  <xsl:template match="/IA/Credits">
      <p><xsl:apply-templates/></p>
  </xsl:template>

  <xsl:template match="/IA/Credits/CopyrightBlock">
      <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="/IA/Credits/CopyrightDate">
      <span><xsl:text>&#169; </xsl:text><xsl:value-of select="text()"/></span>
  </xsl:template>

  <!-- Modules -->

  <xsl:template match="/IA/Modules">
      <h1>Modules (<xsl:number value-of="count(*)"/>)</h1>
      <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="/IA/Modules/Module/Title">
    <xsl:element name="h1">
      <xsl:attribute name="class">title-module</xsl:attribute>
      <xsl:attribute name="id">ref-<xsl:value-of select="../@xy:guid"/></xsl:attribute>
      Module: <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <!-- Lessons -->

  <xsl:template match="/IA/Modules/Module/Lesson/Title">
    <xsl:element name="h2">
      <xsl:attribute name="class">title-lesson</xsl:attribute>
      <xsl:attribute name="id">ref-<xsl:value-of select="../@xy:guid"/></xsl:attribute>
      Lesson: <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="/IA/Modules/Module/Lesson/Topic">
    <div class="topic"><xsl:apply-templates/></div>
    <hr/>
  </xsl:template>

  <!-- Topics -->

  <xsl:template match="/IA/Modules/Module/Lesson/Topic/Title">
    <xsl:element name="h3">
      <xsl:attribute name="class">title-topic</xsl:attribute>
      <xsl:attribute name="id">ref-<xsl:value-of select="../@xy:guid"/></xsl:attribute>
      Topic: <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <!-- Misc -->

  <xsl:template match="//CustomNote">
      <aside class="custom-note"><xsl:apply-templates/></aside>
  </xsl:template>

  <xsl:template match="//CustomNote//SimpleBlock">
    <div class="simple-block"><xsl:apply-templates/></div>
  </xsl:template>

  <xsl:template match="//TitledBlock/Title">
    <span class="title"><strong><xsl:apply-templates/></strong></span>
  </xsl:template>

  <!-- <xsl:template match="//Figure">
    <div class="figure">
      <xsl:apply-templates/>
    </div>
  </xsl:template> -->

  <!-- <xsl:template match="//MediaObject">
    <xsl:apply-templates/>
  </xsl:template> -->

  <!-- <xsl:template match="//MediaObject/Title">
    <p class="italic">Figure - <xsl:apply-templates/></p>
  </xsl:template> -->

  <xsl:template match="//ParaBlock">
    <div class="parablock"><xsl:apply-templates/></div>
  </xsl:template>

  <xsl:template match="//Caption">
    <p class="italic"><xsl:apply-templates/></p>
  </xsl:template>

  <xsl:template match="//Underline">
    <p class="underline"><xsl:apply-templates/></p>
  </xsl:template>

  <xsl:template match="//MediaObject/Renditions/Web">
    <xsl:element name="img">
      <xsl:attribute name="src">
        https://vmware.xyleme.com/editor/media/<xsl:value-of select="translate(@uri, ' ', '+')"/>
      </xsl:attribute>
      <xsl:attribute name="class">image</xsl:attribute>
    </xsl:element>
  </xsl:template>

  <xsl:template match="text">
    <xsl:copy>
      <xsl:call-template name="replace">
        <xsl:with-param name="string" select="."/>
        <xsl:with-param name="search" select="'&#10;'"/>
        <xsl:with-param name="replace"><br/></xsl:with-param>
      </xsl:call-template>
    </xsl:copy>
  </xsl:template>
  
</xsl:stylesheet>

<!--
 148 BoundedText
   1 Callout
   1 IntroBlock
  13 ItemBlock
   5 Lesson
 151 OverlayObject
  14 OverlayObjects
 151 OverlayType
   2 Rect
   1 SubList
   5 TblCol
   2 calloutPoints
-->

