<?xml version="1.0"?>
<!-- Author: Reid
Copyright (C) 2016 Evol Online -->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    >

    <xsl:output method="text" indent="no"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="contributors">
        <xsl:text>.&lt;- @@index|&lt;&lt;Back to Index&gt;&gt;@@&#xa;&#xa;</xsl:text>
        <xsl:text>@@http://evolonline.org/|&lt;&lt;Official site:&gt;&gt; http://evolonline.org@@&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="evol">
        <xsl:text>&#xa;##3---------------------------&#xa;</xsl:text>
        <xsl:text>##3-- &lt;&lt;Evol Online Contributors&gt;&gt; --&#xa;</xsl:text>
        <xsl:text>##3---------------------------&#xa;&#xa;</xsl:text>

        <xsl:apply-templates select="contributor"/>
    </xsl:template>

    <xsl:template match="tmw-ufb">
        <xsl:text>&#xa;##3---------------------------&#xa;</xsl:text>
        <xsl:text>##3-- &lt;&lt;Unknown Flying Bullet Contributors&gt;&gt; --&#xa;</xsl:text>
        <xsl:text>##3---------------------------&#xa;&#xa;</xsl:text>

        <xsl:apply-templates select="contributor"/>
    </xsl:template>

    <xsl:template match="freesound">
        <xsl:text>&#xa;##3---------------------------&#xa;</xsl:text>
        <xsl:text>##3-- &lt;&lt;Freesound Contributors&gt;&gt; --&#xa;</xsl:text>
        <xsl:text>##3---------------------------&#xa;&#xa;</xsl:text>

        <xsl:apply-templates select="contributor"/>
    </xsl:template>

    <xsl:template match="other">
        <xsl:text>&#xa;##3---------------------------&#xa;</xsl:text>
        <xsl:text>##3-- &lt;&lt;Related Communities&gt;&gt; --&#xa;</xsl:text>
        <xsl:text>##3---------------------------&#xa;&#xa;</xsl:text>

        <xsl:apply-templates select="community"/>
    </xsl:template>

    <xsl:template match="contributor">
        <xml:text>##9<xsl:value-of select="@nick"/> </xml:text>
        <xsl:if test="@name">
            <xsl:text> (</xsl:text>
            <xsl:value-of select="@name"/>
            <xsl:text>)</xsl:text>
        </xsl:if>
        <xsl:if test="@mailid">
            <xsl:text> &lt;</xsl:text>
            <xsl:value-of select="@mailid"/>
            <xsl:text>&#160;</xsl:text>
            <xsl:value-of select="@mailserver"/>
            <xsl:text>&gt;</xsl:text>
        </xsl:if>
        <xsl:if test="@page">
            <xsl:text>[@@</xsl:text>
            <xsl:value-of select="@page"/>
            <xsl:text>|&lt;&lt;</xsl:text>
            <xsl:value-of select="@page"/>
            <xsl:text>&gt;&gt;</xsl:text>
            <xsl:text>@@]</xsl:text>
        </xsl:if>
        <xsl:text>&#xa;</xsl:text>
    </xsl:template>

    <xsl:template match="community">
        <xsl:text>[@@</xsl:text>
        <xsl:value-of select="@site"/>
        <xsl:text>|&lt;&lt;</xsl:text>
        <xsl:value-of select="@name"/>
        <xsl:text>&gt;&gt;</xsl:text>
        <xsl:value-of select="@site"/>
        <xsl:text>@@]&#xa;</xsl:text>
    </xsl:template>

</xsl:stylesheet>
