<?xml version="1.0"?>
<!-- Author: Reid
Copyright (C) 2016 Evol Online -->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    >

    <xsl:output method="text" indent="no"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="contributors">
        <xsl:text>[[_TOC_]]&#xa;</xsl:text>
        <xsl:text>****&#xa;&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tmw2">
        <xsl:text>#	TMW2 Contributors&#xa;</xsl:text>
        <xsl:text>|Nickname|Real Name / Email|&#xa;</xsl:text>
        <xsl:text>|--------|-----------------|&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="lof">
        <xsl:text>#	LoF Contributors&#xa;</xsl:text>
        <xsl:text>|Nickname|Notes|&#xa;</xsl:text>
        <xsl:text>|--------|-----|&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="evol">
        <xsl:text>&#xa;</xsl:text>
        <xsl:text>#	Evol Online Contributors&#xa;</xsl:text>
        <xsl:text>|Nickname|Real Name / Email|&#xa;</xsl:text>
        <xsl:text>|--------|-----------------|&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tmw-legacy">
        <xsl:text>&#xa;</xsl:text>
        <xsl:text># The Mana World Legacy Contributors&#xa;</xsl:text>
        <xsl:text>|Nickname|Real Name / Email|&#xa;</xsl:text>
        <xsl:text>|--------|-----------------|&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tmw-ufb">
        <xsl:text>&#xa;</xsl:text>
        <xsl:text>#	Unknown Flying Bullet Contributors&#xa;</xsl:text>
        <xsl:text>|Nickname|Real Name / Email|&#xa;</xsl:text>
        <xsl:text>|--------|-----------------|&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="freesound">
        <xsl:text>&#xa;</xsl:text>
        <xsl:text>#	Freesound Contributors&#xa;</xsl:text>
        <xsl:text>|Nickname|Real Name / Email|&#xa;</xsl:text>
        <xsl:text>|--------|-----------------|&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="other">
        <xsl:text>&#xa;</xsl:text>
        <xsl:text>#	Related Communities&#xa;</xsl:text>
        <xsl:text>&#xa;</xsl:text>

        <xsl:apply-templates select="community"/>
    </xsl:template>

    <xsl:template match="contributor">

        <xsl:text>|</xsl:text>
        <xsl:value-of select="@nick"/>

        <xsl:choose>
            <xsl:when test="@mailid">
                <xsl:text>	|[</xsl:text>
                <xsl:choose>
                    <xsl:when test="@name">
                        <xsl:value-of select="@name"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="@nick"/>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:text>](mailto:</xsl:text>

                <xsl:value-of select="@mailid"/>
                <xsl:text>@</xsl:text>
                <xsl:value-of select="@mailserver"/>
                <xsl:text>)	|</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>	|</xsl:text>
                <xsl:choose>
                    <xsl:when test="@name">
                        <xsl:value-of select="@name"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>No Data</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:text>	|</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#xa;</xsl:text>
    </xsl:template>

    <xsl:template match="community">
        <xsl:text>+ [</xsl:text>
        <xsl:value-of select="@name"/>
        <xsl:text>](</xsl:text>
        <xsl:value-of select="@site"/>
        <xsl:text>)</xsl:text>
        <xsl:text>&#xa;</xsl:text>
    </xsl:template>

    <xsl:template match="sub">
        <xsl:text></xsl:text>
    </xsl:template>

</xsl:stylesheet>

